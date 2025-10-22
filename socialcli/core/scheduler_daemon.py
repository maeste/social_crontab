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
            media_ids = []
            if media_files:
                logger.info(f"Uploading {len(media_files)} media file(s)")
                for media_file in media_files:
                    try:
                        # Handle relative paths - assume relative to post file directory
                        media_path = Path(media_file)
                        if not media_path.is_absolute():
                            media_path = post_path.parent / media_file
                        
                        if not media_path.exists():
                            logger.warning(f"Media file not found: {media_path}")
                            continue
                        
                        logger.info(f"Uploading media: {media_path}")
                        media_urn = provider.upload_media(str(media_path))
                        media_ids.append(media_urn)
                        logger.info(f"Media uploaded successfully: {media_urn}")
                    except Exception as e:
                        logger.error(f"Failed to upload media {media_file}: {e}")
                        # Continue with other media files

            # Execute the post with uploaded media
            kwargs = {}
            if media_ids:
                kwargs['media_ids'] = media_ids
            
            result = provider.post(
                content=parser.content,
                **kwargs
            )

            logger.info(f"Post {post_id} published successfully: {result.get('url', 'N/A')}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute post {post_id}: {e}", exc_info=True)
            return False

    def _process_pending_posts(self):
        """Check for and process all pending posts that are due."""
        try:
            # Get all pending posts
            pending_posts = self.storage.get_all_scheduled_posts(status='pending')

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
