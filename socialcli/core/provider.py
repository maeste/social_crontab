"""
Abstract base class for social media providers.

This module defines the SocialProvider interface that all platform-specific
providers must implement to ensure consistent behavior across different
social media platforms.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class SocialProvider(ABC):
    """
    Abstract base class defining the interface for social media providers.

    All platform-specific providers (LinkedIn, X, Bluesky, etc.) must inherit
    from this class and implement all abstract methods to ensure a consistent
    interface across different social platforms.
    """

    @abstractmethod
    def login(self) -> bool:
        """
        Authenticate with the social media platform.

        This method handles the authentication process, which may vary by platform
        (OAuth 2.0, API keys, etc.). It should store credentials securely and
        establish a session for subsequent API calls.

        Returns:
            bool: True if authentication was successful, False otherwise.

        Raises:
            AuthenticationError: If authentication fails due to invalid credentials
                or connection issues.
        """
        pass

    @abstractmethod
    def post(self, content: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a new post on the social media platform.

        Args:
            content: The text content of the post. May support platform-specific
                formatting (Markdown, mentions, hashtags, etc.).
            **kwargs: Additional platform-specific options such as:
                - media: List of media files to attach
                - visibility: Post visibility settings (public, private, etc.)
                - schedule_time: Time to publish (if scheduling is supported)
                - author: Account/page to post as (for multi-account support)

        Returns:
            Dict containing post metadata:
                - id: Platform-specific post identifier
                - url: Direct URL to the post
                - created_at: Timestamp of post creation
                - status: Post status (published, scheduled, etc.)

        Raises:
            PostError: If post creation fails due to content issues, rate limits,
                or platform errors.
        """
        pass

    @abstractmethod
    def comment(self, target_id: str, text: str) -> Dict[str, Any]:
        """
        Add a comment to an existing post or content.

        Args:
            target_id: Platform-specific identifier of the post/content to comment on.
            text: The comment text content.

        Returns:
            Dict containing comment metadata:
                - id: Platform-specific comment identifier
                - url: Direct URL to the comment
                - created_at: Timestamp of comment creation
                - parent_id: ID of the post/content being commented on

        Raises:
            CommentError: If commenting fails due to permissions, rate limits,
                or invalid target_id.
        """
        pass

    @abstractmethod
    def repost(self, target_id: str, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Repost/share existing content, optionally with additional commentary.

        Args:
            target_id: Platform-specific identifier of the content to repost.
            text: Optional additional commentary to include with the repost.
                Some platforms require commentary, others allow empty reposts.

        Returns:
            Dict containing repost metadata:
                - id: Platform-specific repost identifier
                - url: Direct URL to the repost
                - created_at: Timestamp of repost creation
                - original_id: ID of the content being reposted

        Raises:
            RepostError: If reposting fails due to permissions, rate limits,
                or invalid target_id.
        """
        pass
