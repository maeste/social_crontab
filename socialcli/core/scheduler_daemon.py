"""Scheduler daemon for executing scheduled posts.

Uses the Storage JSON backend to manage scheduled posts and executes them
at the appropriate times using the configured providers.
"""

import time
import signal
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from socialcli.core.storage import Storage
from socialcli.core.config import Config
from socialcli.utils.parser import PostParser


logger = logging.getLogger(__name__)


class SchedulerDaemon:
    """Background daemon that executes scheduled posts at the correct times."""

    def __init__(
        self,
        storage: Optional[Storage] = None,
        check_interval: int = 60
    ):
        """Initialize the scheduler daemon.

        Args:
            storage: Storage instance to use. If None, creates a new one.
            check_interval: How often to check for pending posts (seconds)
        """
        # Configure logging first with DEBUG level
        import os
        log_level = os.environ.get('SOCIALCLI_LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ],
            force=True  # Force reconfiguration even if already configured
        )
        
        self.storage = storage or Storage()
        self.check_interval = check_interval
        self.running = False
        self.config = Config.load(validate=False)

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal, stopping scheduler...")
        self.running = False

    def _get_provider(self, provider_name: str):
        """Initialize and return a provider instance.

        Args:
            provider_name: Name of the provider (e.g., 'linkedin')

        Returns:
            Provider instance

        Raises:
            ValueError: If provider is not supported or not configured
        """
        if provider_name.lower() == 'linkedin':
            from socialcli.providers.linkedin.provider import LinkedInProvider

            # Get provider config
            provider_config = self.config.get_provider_config('linkedin')
            if not provider_config:
                raise ValueError("LinkedIn provider not configured")

            # Create provider with credentials from config
            return LinkedInProvider(
                client_id=provider_config.client_id,
                client_secret=provider_config.client_secret,
                config=self.config
            )
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def _execute_post(self, post_data: dict) -> bool:
        """Execute a single scheduled post.

        Args:
            post_data: Post dictionary from storage

        Returns:
            True if post was successful, False otherwise
        """
        post_id = post_data['id']
        provider_name = post_data['provider']
        file_path = post_data['file_path']

        try:
            logger.info(f"Executing post {post_id} from {file_path}")

            # Read and parse the post file
            post_path = Path(file_path)
            if not post_path.exists():
                logger.error(f"Post file not found: {file_path}")
                return False

            # Parse the post file
            parser = PostParser(file_path)
            media_files = parser.metadata.get('media', [])

            # Initialize provider
            provider = self._get_provider(provider_name)

            # Upload media files if present
            # All-or-nothing policy: if any media upload fails, the entire post fails
            media_ids = []
            media_titles = []
            if media_files:
                logger.info(f"Uploading {len(media_files)} media file(s)")
                for media_file in media_files:
                    # Handle relative paths - assume relative to post file directory
                    media_path = Path(media_file)
                    if not media_path.is_absolute():
                        media_path = post_path.parent / media_file

                    # Fail immediately if media file doesn't exist
                    if not media_path.exists():
                        error_msg = f"Media file not found: {media_path}"
                        logger.error(error_msg)
                        raise FileNotFoundError(error_msg)

                    # Upload media - any exception will fail the entire post
                    logger.info(f"Uploading media: {media_path}")
                    media_urn = provider.upload_media(str(media_path))
                    media_ids.append(media_urn)
                    media_titles.append(media_path.name)  # Store filename for documents
                    logger.info(f"Media uploaded successfully: {media_urn}")

                # Verify all media uploaded successfully
                if len(media_ids) != len(media_files):
                    error_msg = f"Media upload incomplete: expected {len(media_files)}, got {len(media_ids)}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

            # Execute the post with uploaded media
            kwargs = {}
            if media_ids:
                kwargs['media_ids'] = media_ids
                kwargs['media_titles'] = media_titles  # Pass titles for documents

            result = provider.post(
                content=parser.content,
                **kwargs
            )

            # Store URN for comment resolution (Task 19)
            if 'id' in result:
                self.storage.update_scheduled_post(post_id, urn=result['id'])
                logger.info(f"Post {post_id} URN stored: {result['id']}")

            logger.info(f"Post {post_id} published successfully: {result.get('url', 'N/A')}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute post {post_id}: {e}", exc_info=True)
            return False

    def _process_posts(self):
        """Check for and process all pending posts (not comments) that are due."""
        try:
            # Get all pending items
            pending_items = self.storage.get_all_scheduled_posts(status='pending')

            # Filter for posts only (not comments)
            pending_posts = [item for item in pending_items if item.get('type') == 'post']

            if not pending_posts:
                return

            now = datetime.now()

            # Filter posts that are due
            due_posts = []
            for post in pending_posts:
                publish_at = datetime.fromisoformat(post['publish_at'])
                if publish_at <= now:
                    due_posts.append(post)

            if not due_posts:
                return

            logger.info(f"Found {len(due_posts)} post(s) due for publishing")

            # Execute each due post
            for post in due_posts:
                post_id = post['id']
                success = self._execute_post(post)

                # Update status based on result
                new_status = 'published' if success else 'failed'
                self.storage.update_scheduled_post(post_id, status=new_status)
                logger.info(f"Post {post_id} status updated to: {new_status}")

        except Exception as e:
            logger.error(f"Error processing pending posts: {e}", exc_info=True)

    def _process_comments(self):
        """Check for and process all pending comments that are due.

        Validates that parent post is published before attempting to post comment.
        Comments are deferred if parent is not yet published.
        """
        try:
            # Get pending comments that are due
            pending_comments = self.storage.get_pending_comments()

            if not pending_comments:
                return

            logger.info(f"Found {len(pending_comments)} comment(s) due for processing")

            # Process each comment
            for comment in pending_comments:
                comment_id = comment['id']
                parent_uuid = comment.get('parent_uuid')

                if not parent_uuid:
                    logger.error(f"Comment {comment_id} has no parent_uuid")
                    self.storage.update_scheduled_post(
                        comment_id,
                        status='failed',
                        blocked_reason='No parent_uuid specified'
                    )
                    continue

                # Get parent post
                parent = self.storage.get_post_by_uuid(parent_uuid)

                if not parent:
                    logger.error(f"Parent post {parent_uuid} not found for comment {comment_id}")
                    self.storage.update_scheduled_post(
                        comment_id,
                        status='failed',
                        blocked_reason=f'Parent post {parent_uuid} not found'
                    )
                    continue

                # Check parent status
                parent_status = parent.get('status')
                parent_id = parent.get('id')

                if parent_status == 'published':
                    # Parent is published - ready to post comment
                    logger.info(
                        f"Comment {comment_id} ready to post (parent post {parent_id} published)"
                    )
                    success = self._execute_comment(comment, parent)

                    # Update status based on result
                    new_status = 'published' if success else 'failed'
                    self.storage.update_scheduled_post(comment_id, status=new_status)
                    logger.info(f"Comment {comment_id} status updated to: {new_status}")

                elif parent_status == 'failed':
                    # Parent failed - fail this comment too
                    logger.warning(
                        f"Failing comment {comment_id} - parent post {parent_id} failed to publish"
                    )
                    self.storage.update_scheduled_post(
                        comment_id,
                        status='failed',
                        blocked_reason=f'Parent post {parent_id} failed to publish'
                    )

                else:
                    # Parent not yet published (pending or other status) - defer
                    logger.info(
                        f"Deferring comment {comment_id} - parent post {parent_id} "
                        f"not yet published (status: {parent_status})"
                    )
                    # Leave as pending - will be retried on next scheduler run

        except Exception as e:
            logger.error(f"Error processing pending comments: {e}", exc_info=True)

    def _execute_comment(self, comment_data: dict, parent_data: dict) -> bool:
        """Execute a single scheduled comment.

        Retrieves parent post URN and posts comment using provider.

        Args:
            comment_data: Comment dictionary from storage
            parent_data: Parent post dictionary from storage

        Returns:
            True if comment was successful, False otherwise
        """
        comment_id = comment_data['id']
        parent_id = parent_data['id']
        file_path = comment_data['file_path']
        provider_name = comment_data['provider']
        scheduled_time = comment_data.get('publish_at', 'N/A')

        try:
            # Validate parent URN exists
            parent_urn = parent_data.get('urn')
            if not parent_urn:
                error_msg = f"Parent post {parent_id} has no URN available"
                logger.error(
                    f"Failed to post comment {comment_id} "
                    f"(parent: {parent_id}, scheduled: {scheduled_time}): {error_msg}"
                )
                self.storage.update_scheduled_post(
                    comment_id,
                    blocked_reason=error_msg
                )
                return False

            logger.info(f"Executing comment {comment_id} on parent post {parent_id} (URN: {parent_urn})")

            # Read and parse the comment file
            comment_path = Path(file_path)
            if not comment_path.exists():
                error_msg = f"Comment file not found: {file_path}"
                logger.error(
                    f"Failed to post comment {comment_id} "
                    f"(parent: {parent_id}, scheduled: {scheduled_time}): {error_msg}"
                )
                return False

            # Parse the comment file
            parser = PostParser(file_path)
            comment_text = parser.content

            # Initialize provider
            provider = self._get_provider(provider_name)

            # Post the comment
            result = provider.comment(
                target_id=parent_urn,
                text=comment_text
            )

            # Store comment URN if available
            if 'id' in result:
                self.storage.update_scheduled_post(comment_id, urn=result['id'])
                logger.info(f"Comment {comment_id} URN stored: {result['id']}")

            logger.info(f"Comment {comment_id} posted successfully on post {parent_id}")
            return True

        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Failed to post comment {comment_id} "
                f"(parent: {parent_id}, scheduled: {scheduled_time}): {error_msg}",
                exc_info=True
            )
            return False

    def _process_pending_posts(self):
        """Check for and process all pending posts and comments that are due.

        Orchestrates both post and comment processing.
        """
        self._process_posts()
        self._process_comments()

    def run(self):
        """Run the scheduler daemon in a continuous loop.

        Checks for pending posts at regular intervals and executes them
        when their scheduled time arrives. Runs until interrupted.
        """
        self.running = True
        logger.info(f"Scheduler daemon started (check interval: {self.check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        while self.running:
            try:
                self._process_pending_posts()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Unexpected error in scheduler loop: {e}", exc_info=True)
                time.sleep(self.check_interval)

        logger.info("Scheduler daemon stopped")

    def run_once(self):
        """Process pending posts once without entering continuous loop.

        Useful for testing or manual execution.
        """
        logger.info("Running scheduler once...")
        self._process_pending_posts()
        logger.info("Scheduler run completed")
