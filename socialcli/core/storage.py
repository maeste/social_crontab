"""Storage and logging management for SocialCLI.

Handles local file storage for posts, media, and logs.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import fcntl
import os
import uuid


class Storage:
    """Manages local storage for SocialCLI data."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize storage manager.

        Args:
            base_path: Base directory for storage. Defaults to ~/.socialcli
        """
        if base_path is None:
            base_path = Path.home() / '.socialcli'

        self.base_path = base_path
        self.posts_dir = self.base_path / 'posts'
        self.media_dir = self.base_path / 'media'
        self.logs_dir = self.base_path / 'logs'
        self.scheduled_posts_file = self.base_path / 'scheduled_posts.json'

        # UUID index for O(1) lookups
        self._uuid_index: Dict[str, Dict[str, Any]] = {}

        self._init_directories()
        self._init_scheduled_posts()

    def _init_directories(self):
        """Create storage directories if they don't exist."""
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def save_post(self, content: str, filename: str) -> Path:
        """Save post content to storage.

        Args:
            content: Post content
            filename: Filename for the post

        Returns:
            Path to saved file
        """
        file_path = self.posts_dir / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path

    def get_post(self, filename: str) -> str:
        """Retrieve post content from storage.

        Args:
            filename: Name of the post file

        Returns:
            Post content

        Raises:
            FileNotFoundError: If post doesn't exist
        """
        file_path = self.posts_dir / filename
        return file_path.read_text(encoding='utf-8')

    def save_media(self, data: bytes, filename: str) -> Path:
        """Save media file to storage.

        Args:
            data: Binary media data
            filename: Filename for the media

        Returns:
            Path to saved file
        """
        file_path = self.media_dir / filename
        file_path.write_bytes(data)
        return file_path

    def _init_scheduled_posts(self):
        """Initialize scheduled posts JSON file if it doesn't exist."""
        if not self.scheduled_posts_file.exists():
            self.scheduled_posts_file.write_text(
                json.dumps({"posts": []}, indent=2),
                encoding='utf-8'
            )

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a new UUID for a post/comment.

        Returns:
            UUID string
        """
        return str(uuid.uuid4())

    def _ensure_post_fields(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure post has all required fields (lazy migration).

        Args:
            post: Post dictionary

        Returns:
            Post dictionary with all fields
        """
        # Add uuid if missing
        if 'uuid' not in post:
            post['uuid'] = self._generate_uuid()

        # Add type if missing (default to "post")
        if 'type' not in post:
            post['type'] = 'post'

        # Add urn if missing (default to None)
        if 'urn' not in post:
            post['urn'] = None

        # Add parent_uuid if missing (default to None)
        if 'parent_uuid' not in post:
            post['parent_uuid'] = None

        # Add blocked_reason if missing (default to None)
        if 'blocked_reason' not in post:
            post['blocked_reason'] = None

        return post

    def _build_uuid_index(self, posts: List[Dict[str, Any]]):
        """Build UUID index for O(1) lookups.

        Args:
            posts: List of post dictionaries
        """
        self._uuid_index = {}
        for post in posts:
            # Ensure post has uuid before indexing
            self._ensure_post_fields(post)
            self._uuid_index[post['uuid']] = post

    def _read_scheduled_posts(self) -> Dict[str, Any]:
        """Read scheduled posts from JSON file with file locking.

        Performs lazy migration and builds UUID index.

        Returns:
            Dictionary containing scheduled posts data
        """
        with open(self.scheduled_posts_file, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # Lazy migration: ensure all posts have required fields
        migrated = False
        for post in data['posts']:
            original_keys = set(post.keys())
            self._ensure_post_fields(post)
            if set(post.keys()) != original_keys:
                migrated = True

        # Build UUID index for O(1) lookups
        self._build_uuid_index(data['posts'])

        # Save if migration occurred
        if migrated:
            self._write_scheduled_posts(data)

        return data

    def _write_scheduled_posts(self, data: Dict[str, Any]):
        """Write scheduled posts to JSON file with file locking.

        Rebuilds UUID index after writing.

        Args:
            data: Dictionary containing scheduled posts data
        """
        with open(self.scheduled_posts_file, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, ensure_ascii=False)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # Rebuild UUID index
        self._build_uuid_index(data['posts'])

    def create_scheduled_post(
        self,
        provider: str,
        author: str,
        file_path: str,
        publish_at: str,
        status: str = "pending",
        uuid_str: Optional[str] = None,
        post_type: str = "post",
        parent_uuid: Optional[str] = None,
        urn: Optional[str] = None,
        blocked_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new scheduled post or comment.

        Args:
            provider: Social media provider (e.g., 'linkedin')
            author: Author identifier
            file_path: Path to post content file
            publish_at: ISO format datetime string for publishing
            status: Post status (default: 'pending')
            uuid_str: Optional UUID (auto-generated if not provided)
            post_type: Type of post ("post" or "comment", default: "post")
            parent_uuid: For comments, UUID of parent post
            urn: LinkedIn URN (set after publication)
            blocked_reason: Reason if comment is blocked from posting

        Returns:
            Dictionary with 'id' and 'uuid' of the created post

        Raises:
            ValueError: If validation fails
        """
        # Validate type
        if post_type not in ["post", "comment"]:
            raise ValueError(f"Invalid post type: {post_type}. Must be 'post' or 'comment'")

        # Validate: comments must have parent_uuid, posts must not
        if post_type == "comment" and not parent_uuid:
            raise ValueError("Comments must have a parent_uuid")
        if post_type == "post" and parent_uuid:
            raise ValueError("Posts cannot have a parent_uuid")

        # Validate parent exists if comment
        if post_type == "comment":
            parent = self.get_post_by_uuid(parent_uuid)
            if not parent:
                raise ValueError(f"Parent post with UUID {parent_uuid} not found")

            # Validate timing: comment must be >= parent + 5 minutes
            parent_time = datetime.fromisoformat(parent['publish_at'])
            comment_time = datetime.fromisoformat(publish_at)
            min_delay = timedelta(minutes=5)

            if comment_time < parent_time + min_delay:
                raise ValueError(
                    f"Comment must be scheduled at least 5 minutes after parent post. "
                    f"Parent: {parent['publish_at']}, Comment: {publish_at}"
                )

        data = self._read_scheduled_posts()

        # Generate new ID and UUID
        post_id = max([p['id'] for p in data['posts']], default=0) + 1
        if not uuid_str:
            uuid_str = self._generate_uuid()

        # Create new post
        new_post = {
            'id': post_id,
            'uuid': uuid_str,
            'type': post_type,
            'provider': provider,
            'author': author,
            'file_path': file_path,
            'publish_at': publish_at,
            'status': status,
            'urn': urn,
            'parent_uuid': parent_uuid,
            'blocked_reason': blocked_reason,
            'created_at': datetime.now().isoformat()
        }

        data['posts'].append(new_post)
        self._write_scheduled_posts(data)

        return {'id': post_id, 'uuid': uuid_str}

    def get_scheduled_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get a scheduled post by ID.

        Args:
            post_id: ID of the post to retrieve

        Returns:
            Post dictionary or None if not found
        """
        data = self._read_scheduled_posts()
        for post in data['posts']:
            if post['id'] == post_id:
                return post
        return None

    def get_all_scheduled_posts(
        self,
        status: Optional[str] = None,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all scheduled posts, optionally filtered.

        Args:
            status: Filter by status (e.g., 'pending', 'published', 'failed')
            provider: Filter by provider (e.g., 'linkedin')

        Returns:
            List of post dictionaries
        """
        data = self._read_scheduled_posts()
        posts = data['posts']

        if status:
            posts = [p for p in posts if p['status'] == status]
        if provider:
            posts = [p for p in posts if p['provider'] == provider]

        return posts

    def get_post_by_uuid(self, uuid_str: str) -> Optional[Dict[str, Any]]:
        """Get a scheduled post by UUID.

        Args:
            uuid_str: UUID of the post to retrieve

        Returns:
            Post dictionary or None if not found
        """
        # Read to ensure index is built and migrations are applied
        self._read_scheduled_posts()

        # Use O(1) index lookup
        return self._uuid_index.get(uuid_str)

    def get_comments_for_post(self, parent_uuid: str) -> List[Dict[str, Any]]:
        """Get all comments for a given parent post.

        Args:
            parent_uuid: UUID of the parent post

        Returns:
            List of comment dictionaries
        """
        data = self._read_scheduled_posts()

        # Filter for comments with matching parent_uuid
        comments = [
            p for p in data['posts']
            if p.get('type') == 'comment' and p.get('parent_uuid') == parent_uuid
        ]

        return comments

    def get_pending_comments(self, before_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending comments ready to be posted.

        Args:
            before_time: ISO format datetime. Get comments scheduled before this time.
                        If None, uses current time.

        Returns:
            List of comment dictionaries, sorted by publish_at
        """
        if before_time is None:
            before_time = datetime.now().isoformat()

        data = self._read_scheduled_posts()

        # Filter for pending comments scheduled before the specified time
        comments = [
            p for p in data['posts']
            if p.get('type') == 'comment'
            and p.get('status') == 'pending'
            and p.get('publish_at') <= before_time
        ]

        # Sort by publish_at time
        comments.sort(key=lambda x: x.get('publish_at', ''))

        return comments

    def update_scheduled_post(self, post_id: int, **kwargs) -> bool:
        """Update a scheduled post.

        Args:
            post_id: ID of the post to update
            **kwargs: Fields to update (status, publish_at, etc.)

        Returns:
            True if post was updated, False if not found
        """
        data = self._read_scheduled_posts()

        for post in data['posts']:
            if post['id'] == post_id:
                post.update(kwargs)
                post['updated_at'] = datetime.now().isoformat()
                self._write_scheduled_posts(data)
                return True

        return False

    def delete_scheduled_post(self, post_id: int) -> bool:
        """Delete a scheduled post.

        Args:
            post_id: ID of the post to delete

        Returns:
            True if post was deleted, False if not found
        """
        data = self._read_scheduled_posts()
        original_length = len(data['posts'])

        data['posts'] = [p for p in data['posts'] if p['id'] != post_id]

        if len(data['posts']) < original_length:
            self._write_scheduled_posts(data)
            return True

        return False

    def prune_scheduled_posts(
        self,
        before: Optional[str] = None,
        after: Optional[str] = None,
        status: str = "published"
    ) -> int:
        """Prune scheduled posts by date and status.

        Args:
            before: ISO format date - prune posts published before this date
            after: ISO format date - prune posts published after this date
            status: Only prune posts with this status (default: 'published')

        Returns:
            Number of posts pruned
        """
        data = self._read_scheduled_posts()
        original_count = len(data['posts'])

        def should_prune(post: Dict[str, Any]) -> bool:
            # Only prune posts with matching status
            if post.get('status') != status:
                return False

            publish_at = post.get('publish_at')
            if not publish_at:
                return False

            # Check date filters
            if before and publish_at >= before:
                return False
            if after and publish_at <= after:
                return False

            return True

        data['posts'] = [p for p in data['posts'] if not should_prune(p)]
        pruned_count = original_count - len(data['posts'])

        if pruned_count > 0:
            self._write_scheduled_posts(data)

        return pruned_count


class Logger:
    """Configures and manages logging for SocialCLI."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize logger.

        Args:
            log_dir: Directory for log files. Defaults to ~/.socialcli/logs
        """
        if log_dir is None:
            log_dir = Path.home() / '.socialcli' / 'logs'

        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / 'socialcli.log'

        self._configure_logging()

    def _configure_logging(self):
        """Configure logging with file and console handlers."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Logger instance
        """
        return logging.getLogger(name)
