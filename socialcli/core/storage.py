"""Storage and logging management for SocialCLI.

Handles local file storage for posts, media, and logs.
"""

import logging
from pathlib import Path
from typing import Optional
import json


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

        self._init_directories()

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
