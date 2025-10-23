"""LinkedIn provider implementation.

Implements the SocialProvider interface for LinkedIn.
"""

from typing import Optional, Dict, Any
import os
import mimetypes
import requests
from urllib.parse import quote

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

        # Debug: log content before sending
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Posting content (length: {len(content)} chars)")
        logger.debug(f"Full content:\n{content}")

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
            media_ids = kwargs['media_ids'] if isinstance(kwargs['media_ids'], list) else [kwargs['media_ids']]

            if media_ids:
                num_media = len(media_ids)
                logger.info(f"Attaching {num_media} media item(s)")

                # Check if first media is a document (different format required)
                is_document = media_ids[0].startswith('urn:li:document:')

                if is_document and num_media == 1:
                    # Document: requires title field
                    # Extract filename from kwargs if provided, otherwise use generic title
                    document_title = kwargs.get('media_titles', ['Document'])[0] if 'media_titles' in kwargs else 'Document'
                    post_data["content"] = {
                        "media": {
                            "title": document_title,
                            "id": media_ids[0]
                        }
                    }
                elif num_media >= 2:
                    # Multiple images: use multiImage format (2-20 images)
                    post_data["content"] = {
                        "multiImage": {
                            "images": [
                                {"id": media_id}
                                for media_id in media_ids[:20]  # LinkedIn supports up to 20
                            ]
                        }
                    }
                else:
                    # Single image/video: simple media format with just ID
                    post_data["content"] = {
                        "media": {
                            "id": media_ids[0]
                        }
                    }

        # Debug: log payload
        import json
        logger.debug(f"Request payload:\n{json.dumps(post_data, indent=2, ensure_ascii=False)}")

        try:
            response = self.client.post(
                "posts",
                use_rest_api=True,
                json=post_data
            )

            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response body: {response.text}")

            # Extract post ID from response headers or body
            result = response.json() if response.text else {}

            # LinkedIn REST API returns post ID in x-restli-id header
            post_id = response.headers.get('x-restli-id')
            if post_id:
                result['id'] = post_id
                logger.info(f"Post created with ID: {post_id}")

            return result

        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') and e.response else 'N/A'}")
            raise PostError(f"Failed to create post: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
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
            # URL-encode the URN for use in the path
            encoded_urn = quote(target_id, safe='')
            response = self.client.post(
                f"socialActions/{encoded_urn}/comments",
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

    def _detect_media_type(self, file_path: str) -> str:
        """Detect media type from file path.

        Args:
            file_path: Path to media file

        Returns:
            Media type: 'image', 'video', or 'document'

        Raises:
            UploadError: If file type is unsupported
        """
        if not os.path.exists(file_path):
            raise UploadError(f"File not found: {file_path}")

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type is None:
            # Fallback to extension check
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return 'image'
            elif ext in ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.webm', '.mkv']:
                return 'video'
            elif ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']:
                return 'document'
            else:
                raise UploadError(f"Unsupported file type: {ext}")

        # Check MIME type
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type in ['application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/vnd.ms-powerpoint',
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
            return 'document'
        else:
            raise UploadError(f"Unsupported media type: {mime_type}")

    def upload_media(self, file_path: str) -> str:
        """Upload image or video to LinkedIn using the client.

        Supports images (jpg, png, gif) and videos (mp4, mov).
        Uses LinkedIn's asset registration API with appropriate recipes
        for each media type.

        Args:
            file_path: Path to media file (image or video)

        Returns:
            Media URN for use in posts (image or video URN, not asset URN)

        Raises:
            AuthenticationError: If not authenticated
            UploadError: If upload fails or file type is unsupported
        """
        import logging
        logger = logging.getLogger(__name__)

        if not self._person_urn:
            self.login()

        # Detect media type
        media_type = self._detect_media_type(file_path)

        # Route documents to document upload API
        if media_type == 'document':
            return self.upload_document(file_path)

        # Select appropriate recipe based on media type (image/video)
        if media_type == 'image':
            recipe = "urn:li:digitalmediaRecipe:feedshare-image"
        else:  # video
            recipe = "urn:li:digitalmediaRecipe:feedshare-video"

        # Register upload using v2 API (assets endpoint still uses v2)
        register_data = {
            "registerUploadRequest": {
                "recipes": [recipe],
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
            logger.debug(f"Registering upload for file: {file_path}")
            logger.debug(f"Registration payload: {register_data}")

            response = self.client.post(
                "assets?action=registerUpload",
                use_rest_api=False,  # Use v2 API for assets
                json=register_data
            )

            logger.debug(f"Registration response status: {response.status_code}")
            logger.debug(f"Registration response headers: {dict(response.headers)}")
            logger.debug(f"Registration response body: {response.text}")

            upload_info = response.json()

            upload_url = upload_info['value']['uploadMechanism'][
                'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'
            ]['uploadUrl']

            asset_urn = upload_info['value']['asset']
            logger.debug(f"Upload URL: {upload_url}")
            logger.debug(f"Asset URN: {asset_urn}")

            # Upload file directly to LinkedIn's upload URL
            # Get file size for Content-Length header
            file_size = os.path.getsize(file_path)

            with open(file_path, 'rb') as f:
                headers = {
                    'Authorization': f'Bearer {self.client.access_token}',
                    'Content-Length': str(file_size)
                }

                # Videos may require additional headers
                if media_type == 'video':
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type:
                        headers['Content-Type'] = mime_type

                logger.debug(f"Uploading file to LinkedIn, size: {file_size} bytes")
                logger.debug(f"Upload headers: {headers}")

                upload_response = requests.put(
                    upload_url,
                    data=f,
                    headers=headers
                )

                logger.debug(f"Upload response status: {upload_response.status_code}")
                logger.debug(f"Upload response headers: {dict(upload_response.headers)}")
                logger.debug(f"Upload response body: {upload_response.text}")

                upload_response.raise_for_status()

            # Convert digitalmediaAsset URN to image/video URN
            # LinkedIn expects urn:li:image:... or urn:li:video:... for posts
            # Extract the ID from the asset URN and create the correct type
            if asset_urn.startswith('urn:li:digitalmediaAsset:'):
                asset_id = asset_urn.split(':')[-1]
                if media_type == 'image':
                    media_urn = f"urn:li:image:{asset_id}"
                else:
                    media_urn = f"urn:li:video:{asset_id}"
                return media_urn

            # Fallback: return asset URN as-is
            return asset_urn

        except AuthenticationError:
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}", exc_info=True)
            raise UploadError(f"File not found: {str(e)}")
        except requests.HTTPError as e:
            logger.error(f"HTTP error during upload: {e}", exc_info=True)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response status: {e.response.status_code}")
                logger.error(f"Error response headers: {dict(e.response.headers)}")
                logger.error(f"Error response body: {e.response.text}")
            raise UploadError(f"Upload failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}", exc_info=True)
            raise UploadError(f"Failed to upload media: {str(e)}")

    def upload_document(self, file_path: str) -> str:
        """Upload document (PDF, DOC, PPT, etc.) to LinkedIn using Documents API.

        Supports documents up to 100MB and 300 pages.
        Uses LinkedIn's Documents API with two-step upload process.

        Args:
            file_path: Path to document file

        Returns:
            Document URN for use in posts (urn:li:document:xxx)

        Raises:
            AuthenticationError: If not authenticated
            UploadError: If upload fails or file is invalid
        """
        import logging
        logger = logging.getLogger(__name__)

        if not self._person_urn:
            self.login()

        # Validate file
        if not os.path.exists(file_path):
            raise UploadError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB

        if file_size > max_size:
            raise UploadError(f"File too large: {file_size} bytes (max: {max_size})")

        logger.debug(f"Uploading document: {file_path} ({file_size} bytes)")

        try:
            # Step 1: Initialize document upload
            init_data = {
                "initializeUploadRequest": {
                    "owner": self._person_urn
                }
            }

            logger.debug(f"Initializing document upload with payload: {init_data}")

            # Use /rest base URL (not /v2) with required headers
            init_response = self.client.post(
                "documents?action=initializeUpload",
                base_url="https://api.linkedin.com/rest",
                json=init_data,
                headers={
                    "Linkedin-Version": "202509",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
            )

            logger.debug(f"Initialize response status: {init_response.status_code}")
            logger.debug(f"Initialize response headers: {dict(init_response.headers)}")
            logger.debug(f"Initialize response body: {init_response.text}")

            init_result = init_response.json()
            upload_url = init_result['value']['uploadUrl']
            document_urn = init_result['value']['document']

            logger.debug(f"Upload URL: {upload_url}")
            logger.debug(f"Document URN: {document_urn}")

            # Step 2: Upload file to the provided URL
            with open(file_path, 'rb') as f:
                headers = {
                    'Authorization': f'Bearer {self.client.access_token}'
                }

                logger.debug(f"Uploading file to LinkedIn, size: {file_size} bytes")

                upload_response = requests.put(
                    upload_url,
                    data=f,
                    headers=headers
                )

                logger.debug(f"Upload response status: {upload_response.status_code}")
                logger.debug(f"Upload response headers: {dict(upload_response.headers)}")
                logger.debug(f"Upload response body: {upload_response.text}")

                upload_response.raise_for_status()

            logger.info(f"Document uploaded successfully: {document_urn}")
            return document_urn

        except AuthenticationError:
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}", exc_info=True)
            raise UploadError(f"File not found: {str(e)}")
        except requests.HTTPError as e:
            logger.error(f"HTTP error during document upload: {e}", exc_info=True)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response status: {e.response.status_code}")
                logger.error(f"Error response headers: {dict(e.response.headers)}")
                logger.error(f"Error response body: {e.response.text}")
            raise UploadError(f"Document upload failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during document upload: {e}", exc_info=True)
            raise UploadError(f"Failed to upload document: {str(e)}")

    def get_profile(self) -> Dict[str, Any]:
        """Get authenticated user's profile using OpenID Connect userinfo endpoint.

        Returns:
            Dict containing profile information including:
                - sub: LinkedIn member ID
                - name: User's full name
                - given_name: User's first name
                - family_name: User's last name
                - email: User's email address

        Raises:
            AuthenticationError: If not authenticated
        """
        try:
            # Use OpenID Connect userinfo endpoint instead of deprecated /v2/me
            # This endpoint works with openid, profile, email scopes
            response = self.client.get(
                "userinfo",
                use_rest_api=False  # Uses v2 base URL: https://api.linkedin.com/v2/userinfo
            )
            profile_data = response.json()

            # Map OpenID Connect fields to expected format for backward compatibility
            # 'sub' is the LinkedIn member ID in OpenID Connect
            if 'sub' in profile_data and 'id' not in profile_data:
                profile_data['id'] = profile_data['sub']

            return profile_data
        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            raise AuthenticationError(f"Failed to get profile: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Unexpected error getting profile: {str(e)}")

    def get_post(self, post_urn: str) -> Dict[str, Any]:
        """Get a specific post by URN to check its status.

        Args:
            post_urn: Post URN (e.g., 'urn:li:share:7387174250509406208')

        Returns:
            Dict containing post details including status, content, media, etc.

        Raises:
            AuthenticationError: If not authenticated
            Exception: If post retrieval fails
        """
        import logging
        logger = logging.getLogger(__name__)

        if not self._person_urn:
            self.login()

        try:
            # URL encode the URN for the API path
            from urllib.parse import quote
            encoded_urn = quote(post_urn, safe='')

            logger.debug(f"Retrieving post: {post_urn}")
            logger.debug(f"Encoded URN: {encoded_urn}")

            # Use REST API to get the post
            response = self.client.get(
                f"posts/{encoded_urn}",
                use_rest_api=True
            )

            logger.debug(f"Get post response status: {response.status_code}")
            logger.debug(f"Get post response headers: {dict(response.headers)}")
            logger.debug(f"Get post response body: {response.text}")

            post_data = response.json()
            return post_data

        except AuthenticationError:
            raise
        except requests.HTTPError as e:
            logger.error(f"HTTP error retrieving post: {e}", exc_info=True)
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response status: {e.response.status_code}")
                logger.error(f"Error response headers: {dict(e.response.headers)}")
                logger.error(f"Error response body: {e.response.text}")
            raise Exception(f"Failed to retrieve post: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving post: {e}", exc_info=True)
            raise Exception(f"Failed to retrieve post: {str(e)}")
