"""Storage and logging management for SocialCLI.

Handles local file storage for posts, media, and logs.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import fcntl
import os


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

    def _read_scheduled_posts(self) -> Dict[str, Any]:
        """Read scheduled posts from JSON file with file locking.

        Returns:
            Dictionary containing scheduled posts data
        """
        with open(self.scheduled_posts_file, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return data

    def _write_scheduled_posts(self, data: Dict[str, Any]):
        """Write scheduled posts to JSON file with file locking.

        Args:
            data: Dictionary containing scheduled posts data
        """
        with open(self.scheduled_posts_file, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, ensure_ascii=False)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def create_scheduled_post(
        self,
        provider: str,
        author: str,
        file_path: str,
        publish_at: str,
        status: str = "pending"
    ) -> int:
        """Create a new scheduled post.

        Args:
            provider: Social media provider (e.g., 'linkedin')
            author: Author identifier
            file_path: Path to post content file
            publish_at: ISO format datetime string for publishing
            status: Post status (default: 'pending')

        Returns:
            ID of the created post
        """
        data = self._read_scheduled_posts()

        # Generate new ID
        post_id = max([p['id'] for p in data['posts']], default=0) + 1

        # Create new post
        new_post = {
            'id': post_id,
            'provider': provider,
            'author': author,
            'file_path': file_path,
            'publish_at': publish_at,
            'status': status,
            'created_at': datetime.now().isoformat()
        }

        data['posts'].append(new_post)
        self._write_scheduled_posts(data)

        return post_id

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
