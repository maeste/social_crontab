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
from socialcli.providers.linkedin.client import LinkedInAPIClient
from socialcli.providers.linkedin.auth import LinkedInAuth
from socialcli.core.config import Config


class LinkedInProvider(SocialProvider):
    """LinkedIn implementation of SocialProvider.

    Uses LinkedIn REST API v2 for posting, commenting, and media upload.
    Integrates LinkedInAPIClient for robust HTTP handling and LinkedInAuth
    for authentication management.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: str = "http://localhost:8080/callback",
        access_token: Optional[str] = None,
        config: Optional[Config] = None
    ):
        """Initialize LinkedIn provider.

        Args:
            client_id: LinkedIn application client ID (required for auth)
            client_secret: LinkedIn application client secret (required for auth)
            redirect_uri: OAuth callback URI
            access_token: LinkedIn OAuth access token (optional, will use from config if not provided)
            config: Config instance for token storage (optional)
        """
        self.config = config or Config()
        self._user_id = None
        self._person_urn = None

        # Initialize auth if credentials provided
        self.auth = None
        if client_id and client_secret:
            self.auth = LinkedInAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                config=self.config
            )

        # Initialize API client with access token
        if access_token:
            self.client = LinkedInAPIClient(access_token=access_token)
        elif self.auth:
            # Try to get valid token from config
            valid_token = self.auth.get_valid_token()
            self.client = LinkedInAPIClient(access_token=valid_token)
        else:
            self.client = LinkedInAPIClient()

    def login(self) -> bool:
        """Verify authentication by fetching user profile.

        Returns:
            True if authenticated successfully

        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.client.access_token:
            raise AuthenticationError("No access token available. Please authenticate first.")

        try:
            profile = self.get_profile()
            self._user_id = profile.get('id')
            # Store person URN for use in posts
            self._person_urn = f"urn:li:person:{self._user_id}"
            return True
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    def post(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create a LinkedIn post using the REST API.

        Args:
            content: Post text content
            **kwargs: Optional parameters:
                - media_ids: List of media URNs to attach
                - visibility: Post visibility ('PUBLIC', 'CONNECTIONS', 'LOGGED_IN')
                - author_urn: Override author URN (for organization posts)

        Returns:
            Dict containing post details including:
                - id: Post ID/URN
                - created_time: Post creation timestamp

        Raises:
            AuthenticationError: If not authenticated
            PostError: If post creation fails
        """
        if not self._person_urn:
            self.login()

        # Allow override for organization posts
        author_urn = kwargs.get('author_urn', self._person_urn)

        # Build post payload for REST API
        post_data = {
            "author": author_urn,
            "commentary": content,
            "visibility": kwargs.get('visibility', 'PUBLIC'),
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }

        # Add media if provided
        if 'media_ids' in kwargs and kwargs['media_ids']:
            post_data["content"] = {
                "media": {
                    "title": content[:100],  # Use first 100 chars as title
                    "id": kwargs['media_ids'][0]  # LinkedIn REST API supports single media
                }
            }

        try:
            response = self.client.post(
                "posts",
                use_rest_api=True,
                json=post_data
            )

            # Extract post ID from response headers or body
            result = response.json() if response.text else {}

            # LinkedIn REST API returns post ID in x-restli-id header
            post_id = response.headers.get('x-restli-id')
            if post_id:
                result['id'] = post_id

            return result

        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            raise PostError(f"Failed to create post: {str(e)}")
        except Exception as e:
            raise PostError(f"Unexpected error creating post: {str(e)}")

    def comment(self, target_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to a LinkedIn post using REST API.

        Args:
            target_id: URN of the target post (e.g., 'urn:li:share:123456')
            text: Comment text

        Returns:
            Dict containing comment details including:
                - id: Comment ID/URN
                - created_time: Comment creation timestamp

        Raises:
            AuthenticationError: If not authenticated
            CommentError: If comment creation fails
        """
        if not self._person_urn:
            self.login()

        # Build comment payload for REST API
        comment_data = {
            "actor": self._person_urn,
            "message": {
                "text": text
            },
            "object": target_id
        }

        try:
            response = self.client.post(
                "comments",
                use_rest_api=True,
                json=comment_data
            )

            # Extract comment ID from response
            result = response.json() if response.text else {}

            # LinkedIn REST API returns comment ID in x-restli-id header
            comment_id = response.headers.get('x-restli-id')
            if comment_id:
                result['id'] = comment_id

            return result

        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            raise CommentError(f"Failed to create comment: {str(e)}")
        except Exception as e:
            raise CommentError(f"Unexpected error creating comment: {str(e)}")

    def repost(self, target_id: str, text: Optional[str] = None) -> Dict[str, Any]:
        """Share/repost a LinkedIn post using REST API.

        Args:
            target_id: URN of the post to share
            text: Optional commentary text

        Returns:
            Dict containing repost details

        Raises:
            AuthenticationError: If not authenticated
            RepostError: If repost fails
        """
        if not self._person_urn:
            self.login()

        # Build repost payload for REST API
        share_data = {
            "author": self._person_urn,
            "commentary": text or "",
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
            "reshareContext": {
                "parent": target_id
            }
        }

        try:
            response = self.client.post(
                "posts",
                use_rest_api=True,
                json=share_data
            )

            result = response.json() if response.text else {}

            # Extract post ID from response header
            post_id = response.headers.get('x-restli-id')
            if post_id:
                result['id'] = post_id

            return result

        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            raise RepostError(f"Failed to repost: {str(e)}")
        except Exception as e:
            raise RepostError(f"Unexpected error creating repost: {str(e)}")

    def upload_media(self, file_path: str) -> str:
        """Upload image to LinkedIn using the client.

        Args:
            file_path: Path to image file

        Returns:
            Media URN for use in posts

        Raises:
            AuthenticationError: If not authenticated
            UploadError: If upload fails
        """
        if not self._person_urn:
            self.login()

        # Register upload using v2 API (assets endpoint still uses v2)
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self._person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        try:
            # Register upload with v2 API
            response = self.client.post(
                "assets?action=registerUpload",
                use_rest_api=False,  # Use v2 API for assets
                json=register_data
            )

            upload_info = response.json()

            upload_url = upload_info['value']['uploadMechanism'][
                'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'
            ]['uploadUrl']

            asset_urn = upload_info['value']['asset']

            # Upload file directly to LinkedIn's upload URL
            with open(file_path, 'rb') as f:
                upload_response = requests.put(
                    upload_url,
                    data=f,
                    headers={'Authorization': f'Bearer {self.client.access_token}'}
                )
                upload_response.raise_for_status()

            return asset_urn

        except AuthenticationError:
            raise
        except Exception as e:
            raise UploadError(f"Failed to upload media: {str(e)}")

    def get_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile using the client.

        Returns:
            Dict containing profile information including:
                - id: LinkedIn member ID
                - firstName: User's first name
                - lastName: User's last name

        Raises:
            AuthenticationError: If not authenticated
        """
        try:
            response = self.client.get(
                "me",
                use_rest_api=False  # Profile endpoint still uses v2 API
            )
            return response.json()
        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            raise AuthenticationError(f"Failed to get profile: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Unexpected error getting profile: {str(e)}")
