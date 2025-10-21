"""Post file parser for markdown and text files.

Handles parsing of post files with optional YAML front matter.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import yaml


class PostParser:
    """Parses post files with optional front matter."""

    def __init__(self, file_path: str):
        """Initialize parser with file path.

        Args:
            file_path: Path to post file (.md or .txt)
        """
        self.file_path = Path(file_path)
        self.metadata: Dict[str, Any] = {}
        self.content: str = ""

        self._parse()

    def _parse(self):
        """Parse the post file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Post file not found: {self.file_path}")

        file_content = self.file_path.read_text(encoding='utf-8')

        # Check for YAML front matter
        front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(front_matter_pattern, file_content, re.DOTALL)

        if match:
            # Extract front matter and content
            front_matter_text = match.group(1)
            self.content = match.group(2).strip()

            # Parse YAML front matter
            try:
                self.metadata = yaml.safe_load(front_matter_text) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML front matter: {e}")
        else:
            # No front matter, entire file is content
            self.content = file_content.strip()

    def get_title(self) -> Optional[str]:
        """Get post title from metadata.

        Returns:
            Title if present in metadata, None otherwise
        """
        return self.metadata.get('title')

    def get_tags(self) -> list:
        """Get tags from metadata.

        Returns:
            List of tags, or empty list if none
        """
        tags = self.metadata.get('tags', [])
        if isinstance(tags, str):
            # Handle comma-separated tags
            return [tag.strip() for tag in tags.split(',')]
        return tags

    def get_provider(self) -> Optional[str]:
        """Get target provider from metadata.

        Returns:
            Provider name if specified, None otherwise
        """
        return self.metadata.get('provider')

    def get_schedule(self) -> Optional[str]:
        """Get schedule time from metadata.

        Returns:
            ISO format datetime string if schedule specified, None otherwise
        """
        schedule = self.metadata.get('schedule')
        if schedule is None:
            return None

        if isinstance(schedule, datetime):
            return schedule.isoformat()

        if isinstance(schedule, str):
            # Validate ISO format
            try:
                datetime.fromisoformat(schedule)
                return schedule
            except ValueError:
                raise ValueError(f"Invalid schedule format: {schedule}. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

        return None

    def get_content(self) -> str:
        """Get post content.

        Returns:
            Post content text
        """
        return self.content

    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed post to dictionary.

        Returns:
            Dict containing all parsed data
        """
        return {
            'title': self.get_title(),
            'tags': self.get_tags(),
            'provider': self.get_provider(),
            'schedule': self.get_schedule(),
            'content': self.get_content(),
            'metadata': self.metadata
        }

    def has_front_matter(self) -> bool:
        """Check if post has front matter.

        Returns:
            True if front matter exists, False otherwise
        """
        return bool(self.metadata)

    def validate(self) -> bool:
        """Validate parsed post data.

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If content is empty or schedule format is invalid
        """
        if not self.content:
            raise ValueError("Post content cannot be empty")

        # Validate schedule if present
        if self.metadata.get('schedule'):
            self.get_schedule()  # This will raise ValueError if invalid

        return True

    def get_metadata_field(self, field: str, default: Any = None) -> Any:
        """Get a custom metadata field.

        Args:
            field: Field name
            default: Default value if field not found

        Returns:
            Field value or default
        """
        return self.metadata.get(field, default)
