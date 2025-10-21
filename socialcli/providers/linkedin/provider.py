"""LinkedIn provider implementation.

Implements the SocialProvider interface for LinkedIn.
"""

from typing import Optional, Dict, Any
import requests

from socialcli.providers.base import (
    SocialProvider,
    AuthenticationError,
    PostError,
    CommentError,
    RepostError,
    UploadError
)


class LinkedInProvider(SocialProvider):
    """LinkedIn implementation of SocialProvider.

    Uses LinkedIn REST API v2 for posting, commenting, and media upload.
    """

    API_BASE = "https://api.linkedin.com/v2"
    API_REST_BASE = "https://api.linkedin.com/rest"

    def __init__(self, access_token: Optional[str] = None):
        """Initialize LinkedIn provider.

        Args:
            access_token: LinkedIn OAuth access token
        """
        self.access_token = access_token
        self._user_id = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication.

        Returns:
            Dict of HTTP headers

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.access_token:
            raise AuthenticationError("Not authenticated. Please login first.")

        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

    def login(self) -> bool:
        """Verify authentication by fetching user profile.

        Returns:
            True if authenticated successfully

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            profile = self.get_profile()
            self._user_id = profile.get('id')
            return True
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create a LinkedIn post.

        Args:
            content: Post text content
            **kwargs: Optional parameters (media_ids, visibility, etc.)

        Returns:
            Dict containing post details

        Raises:
            AuthenticationError: If not authenticated
            PostError: If post creation fails
        """
        if not self._user_id:
            self.login()

        post_data = {
            "author": f"urn:li:person:{self._user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Add media if provided
        if 'media_ids' in kwargs:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {"status": "READY", "media": media_id}
                for media_id in kwargs['media_ids']
            ]

        try:
            response = requests.post(
                f"{self.API_BASE}/ugcPosts",
                json=post_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise PostError(f"Failed to create post: {str(e)}")

    def comment(self, target_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to a LinkedIn post.

        Args:
            target_id: URN of the target post
            text: Comment text

        Returns:
            Dict containing comment details

        Raises:
            AuthenticationError: If not authenticated
            CommentError: If comment creation fails
        """
        if not self._user_id:
            self.login()

        comment_data = {
            "actor": f"urn:li:person:{self._user_id}",
            "object": target_id,
            "message": {
                "text": text
            }
        }

        try:
            response = requests.post(
                f"{self.API_REST_BASE}/comments",
                json=comment_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise CommentError(f"Failed to create comment: {str(e)}")

    def repost(self, target_id: str, text: Optional[str] = None) -> Dict[str, Any]:
        """Share/repost a LinkedIn post.

        Args:
            target_id: URN of the post to share
            text: Optional commentary text

        Returns:
            Dict containing repost details

        Raises:
            AuthenticationError: If not authenticated
            RepostError: If repost fails
        """
        if not self._user_id:
            self.login()

        share_data = {
            "author": f"urn:li:person:{self._user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareMediaCategory": "NONE",
                    "shareCommentary": {
                        "text": text or ""
                    }
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
            "resharedContent": target_id
        }

        try:
            response = requests.post(
                f"{self.API_BASE}/ugcPosts",
                json=share_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise RepostError(f"Failed to repost: {str(e)}")

    def upload_media(self, file_path: str) -> str:
        """Upload image to LinkedIn.

        Args:
            file_path: Path to image file

        Returns:
            Media URN for use in posts

        Raises:
            AuthenticationError: If not authenticated
            UploadError: If upload fails
        """
        if not self._user_id:
            self.login()

        # Register upload
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{self._user_id}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        try:
            response = requests.post(
                f"{self.API_BASE}/assets?action=registerUpload",
                json=register_data,
                headers=self._get_headers()
            )
            response.raise_for_status()
            upload_info = response.json()

            upload_url = upload_info['value']['uploadMechanism'][
                'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'
            ]['uploadUrl']

            asset_urn = upload_info['value']['asset']

            # Upload file
            with open(file_path, 'rb') as f:
                upload_response = requests.put(
                    upload_url,
                    data=f,
                    headers={'Authorization': f'Bearer {self.access_token}'}
                )
                upload_response.raise_for_status()

            return asset_urn

        except Exception as e:
            raise UploadError(f"Failed to upload media: {str(e)}")

    def get_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile.

        Returns:
            Dict containing profile information

        Raises:
            AuthenticationError: If not authenticated
        """
        try:
            response = requests.get(
                f"{self.API_BASE}/me",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise AuthenticationError(f"Failed to get profile: {str(e)}")
