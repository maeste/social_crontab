"""Base social provider interface.

Defines the abstract base class that all social media providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class SocialProvider(ABC):
    """Abstract base class for social media providers.

    All provider implementations (LinkedIn, X, Bluesky, etc.) must
    inherit from this class and implement all abstract methods.
    """

    @abstractmethod
    def login(self) -> bool:
        """Authenticate with the social media provider.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create a new post.

        Args:
            content: Post content (text, markdown, etc.)
            **kwargs: Provider-specific options (media, visibility, etc.)

        Returns:
            Dict containing post details (id, url, timestamp, etc.)

        Raises:
            AuthenticationError: If not authenticated
            PostError: If post creation fails
        """
        pass

    @abstractmethod
    def comment(self, target_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to a post.

        Args:
            target_id: ID of the target post
            text: Comment text

        Returns:
            Dict containing comment details (id, timestamp, etc.)

        Raises:
            AuthenticationError: If not authenticated
            CommentError: If comment creation fails
        """
        pass

    @abstractmethod
    def repost(self, target_id: str, text: Optional[str] = None) -> Dict[str, Any]:
        """Repost/share a post.

        Args:
            target_id: ID of the post to repost
            text: Optional commentary text

        Returns:
            Dict containing repost details

        Raises:
            AuthenticationError: If not authenticated
            RepostError: If repost fails
        """
        pass

    @abstractmethod
    def upload_media(self, file_path: str) -> str:
        """Upload media file to the provider.

        Args:
            file_path: Path to media file

        Returns:
            Media ID or URL for use in posts

        Raises:
            AuthenticationError: If not authenticated
            UploadError: If upload fails
        """
        pass

    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile information.

        Returns:
            Dict containing profile data

        Raises:
            AuthenticationError: If not authenticated
        """
        pass


class AuthenticationError(Exception):
    """Raised when authentication fails or is required."""
    pass


class PostError(Exception):
    """Raised when post creation fails."""
    pass


class CommentError(Exception):
    """Raised when comment creation fails."""
    pass


class RepostError(Exception):
    """Raised when reposting fails."""
    pass


class UploadError(Exception):
    """Raised when media upload fails."""
    pass
