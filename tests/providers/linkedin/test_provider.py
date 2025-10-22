"""Tests for LinkedIn provider implementation."""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import requests

from socialcli.providers.linkedin.provider import LinkedInProvider
from socialcli.providers.base import (
    AuthenticationError,
    PostError,
    CommentError,
    RepostError,
    UploadError
)


class TestLinkedInProviderInitialization:
    """Test LinkedIn provider initialization."""

    def test_initialization_with_access_token(self):
        """Test provider initializes with access token."""
        provider = LinkedInProvider(access_token="test_token")
        assert provider.client.access_token == "test_token"
        assert provider._user_id is None
        assert provider._person_urn is None

    def test_initialization_with_credentials(self):
        """Test provider initializes with OAuth credentials."""
        provider = LinkedInProvider(
            client_id="test_client_id",
            client_secret="test_secret"
        )
        assert provider.auth is not None
        assert provider.auth.client_id == "test_client_id"
        assert provider.auth.client_secret == "test_secret"

    def test_initialization_without_credentials(self):
        """Test provider initializes without credentials."""
        provider = LinkedInProvider()
        assert provider.client.access_token is None
        assert provider.auth is None


class TestLinkedInProviderLogin:
    """Test login functionality."""

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.get_profile')
    def test_login_success(self, mock_get_profile):
        """Test successful login."""
        mock_get_profile.return_value = {'id': 'test_user_id'}

        provider = LinkedInProvider(access_token="test_token")
        result = provider.login()

        assert result is True
        assert provider._user_id == 'test_user_id'
        assert provider._person_urn == 'urn:li:person:test_user_id'
        mock_get_profile.assert_called_once()

    def test_login_without_token_raises_error(self):
        """Test login without access token raises error."""
        provider = LinkedInProvider()

        with pytest.raises(AuthenticationError, match="No access token available"):
            provider.login()

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.get_profile')
    def test_login_failure_raises_error(self, mock_get_profile):
        """Test login failure raises AuthenticationError."""
        mock_get_profile.side_effect = Exception("API error")

        provider = LinkedInProvider(access_token="test_token")

        with pytest.raises(AuthenticationError, match="Login failed"):
            provider.login()


class TestLinkedInProviderPost:
    """Test post creation functionality."""

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_post_success(self, mock_client_post, mock_login):
        """Test successful post creation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'content': 'Test post'}
        mock_response.text = '{"content": "Test post"}'
        mock_response.headers = {'x-restli-id': 'urn:li:share:123456'}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.post("Test post content")

        assert result['id'] == 'urn:li:share:123456'
        mock_client_post.assert_called_once()

        # Verify post payload structure
        call_args = mock_client_post.call_args
        assert call_args[1]['use_rest_api'] is True
        post_data = call_args[1]['json']
        assert post_data['author'] == 'urn:li:person:test_user'
        assert post_data['commentary'] == 'Test post content'
        assert post_data['visibility'] == 'PUBLIC'

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_post_with_organization_author(self, mock_client_post, mock_login):
        """Test post creation with organization author URN."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.text = '{}'
        mock_response.headers = {'x-restli-id': 'urn:li:share:123456'}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        org_urn = "urn:li:organization:123456"
        result = provider.post("Company update", author_urn=org_urn)

        # Verify organization URN was used
        call_args = mock_client_post.call_args
        post_data = call_args[1]['json']
        assert post_data['author'] == org_urn

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_post_with_media(self, mock_client_post, mock_login):
        """Test post creation with media."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.text = '{}'
        mock_response.headers = {'x-restli-id': 'urn:li:share:123456'}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        media_ids = ["urn:li:digitalmediaAsset:123"]
        result = provider.post("Post with image", media_ids=media_ids)

        # Verify media was included
        call_args = mock_client_post.call_args
        post_data = call_args[1]['json']
        assert 'content' in post_data
        assert 'media' in post_data['content']
        assert post_data['content']['media']['id'] == media_ids[0]

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_post_failure_raises_error(self, mock_client_post, mock_login):
        """Test post creation failure raises PostError."""
        mock_client_post.side_effect = requests.HTTPError("API error")

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        with pytest.raises(PostError, match="Failed to create post"):
            provider.post("Test post")

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    def test_post_calls_login_if_not_authenticated(self, mock_login):
        """Test post calls login if not authenticated."""
        provider = LinkedInProvider(access_token="test_token")

        with patch.object(provider.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.text = '{}'
            mock_response.headers = {}
            mock_post.return_value = mock_response

            provider.post("Test")

            mock_login.assert_called_once()


class TestLinkedInProviderComment:
    """Test comment functionality."""

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_comment_success(self, mock_client_post, mock_login):
        """Test successful comment creation."""
        mock_response = Mock()
        mock_response.json.return_value = {'message': {'text': 'Test comment'}}
        mock_response.text = '{"message": {"text": "Test comment"}}'
        mock_response.headers = {'x-restli-id': 'urn:li:comment:123456'}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.comment("urn:li:share:999", "Great post!")

        assert result['id'] == 'urn:li:comment:123456'
        mock_client_post.assert_called_once()

        # Verify comment payload
        call_args = mock_client_post.call_args
        assert call_args[1]['use_rest_api'] is True
        comment_data = call_args[1]['json']
        assert comment_data['actor'] == 'urn:li:person:test_user'
        assert comment_data['message']['text'] == 'Great post!'
        assert comment_data['object'] == 'urn:li:share:999'

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_comment_failure_raises_error(self, mock_client_post, mock_login):
        """Test comment creation failure raises CommentError."""
        mock_client_post.side_effect = requests.HTTPError("API error")

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        with pytest.raises(CommentError, match="Failed to create comment"):
            provider.comment("urn:li:share:999", "Test comment")


class TestLinkedInProviderRepost:
    """Test repost/share functionality."""

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_repost_success(self, mock_client_post, mock_login):
        """Test successful repost."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.text = '{}'
        mock_response.headers = {'x-restli-id': 'urn:li:share:789'}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.repost("urn:li:share:123", "Check this out!")

        assert result['id'] == 'urn:li:share:789'

        # Verify repost payload
        call_args = mock_client_post.call_args
        post_data = call_args[1]['json']
        assert post_data['author'] == 'urn:li:person:test_user'
        assert post_data['commentary'] == 'Check this out!'
        assert post_data['reshareContext']['parent'] == 'urn:li:share:123'

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_repost_without_commentary(self, mock_client_post, mock_login):
        """Test repost without commentary text."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.text = '{}'
        mock_response.headers = {}
        mock_client_post.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.repost("urn:li:share:123")

        # Verify empty commentary
        call_args = mock_client_post.call_args
        post_data = call_args[1]['json']
        assert post_data['commentary'] == ''

    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_repost_failure_raises_error(self, mock_client_post, mock_login):
        """Test repost failure raises RepostError."""
        mock_client_post.side_effect = requests.HTTPError("API error")

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        with pytest.raises(RepostError, match="Failed to repost"):
            provider.repost("urn:li:share:123")


class TestLinkedInProviderUploadMedia:
    """Test media upload functionality."""

    @patch('mimetypes.guess_type')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    @patch('builtins.open', create=True)
    @patch('requests.put')
    def test_upload_image_success(self, mock_put, mock_open, mock_client_post, mock_login, mock_getsize, mock_exists, mock_guess_type):
        """Test successful image upload."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 100  # 100KB
        mock_guess_type.return_value = ('image/jpeg', None)

        # Mock register upload response
        mock_register_response = Mock()
        mock_register_response.json.return_value = {
            'value': {
                'uploadMechanism': {
                    'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest': {
                        'uploadUrl': 'https://upload.linkedin.com/abc123'
                    }
                },
                'asset': 'urn:li:digitalmediaAsset:123456'
            }
        }
        mock_client_post.return_value = mock_register_response

        # Mock file upload response
        mock_upload_response = Mock()
        mock_upload_response.raise_for_status = Mock()
        mock_put.return_value = mock_upload_response

        # Mock file
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.upload_media("/path/to/image.jpg")

        assert result == 'urn:li:digitalmediaAsset:123456'
        mock_client_post.assert_called_once()

        # Verify image recipe was used
        call_args = mock_client_post.call_args
        register_data = call_args[1]['json']
        assert register_data['registerUploadRequest']['recipes'][0] == 'urn:li:digitalmediaRecipe:feedshare-image'

        mock_put.assert_called_once()
        mock_open.assert_called_once_with('/path/to/image.jpg', 'rb')

    @patch('mimetypes.guess_type')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    @patch('builtins.open', create=True)
    @patch('requests.put')
    def test_upload_video_success(self, mock_put, mock_open, mock_client_post, mock_login, mock_getsize, mock_exists, mock_guess_type):
        """Test successful video upload."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024 * 5  # 5MB
        mock_guess_type.return_value = ('video/mp4', None)

        # Mock register upload response
        mock_register_response = Mock()
        mock_register_response.json.return_value = {
            'value': {
                'uploadMechanism': {
                    'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest': {
                        'uploadUrl': 'https://upload.linkedin.com/video123'
                    }
                },
                'asset': 'urn:li:digitalmediaAsset:video789'
            }
        }
        mock_client_post.return_value = mock_register_response

        # Mock file upload response
        mock_upload_response = Mock()
        mock_upload_response.raise_for_status = Mock()
        mock_put.return_value = mock_upload_response

        # Mock file
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        result = provider.upload_media("/path/to/video.mp4")

        assert result == 'urn:li:digitalmediaAsset:video789'

        # Verify video recipe was used
        call_args = mock_client_post.call_args
        register_data = call_args[1]['json']
        assert register_data['registerUploadRequest']['recipes'][0] == 'urn:li:digitalmediaRecipe:feedshare-video'

    @patch('os.path.exists')
    def test_detect_media_type_image(self, mock_exists):
        """Test media type detection for images."""
        mock_exists.return_value = True

        provider = LinkedInProvider(access_token="test_token")

        # Test various image extensions
        assert provider._detect_media_type("/path/to/file.jpg") == 'image'
        assert provider._detect_media_type("/path/to/file.jpeg") == 'image'
        assert provider._detect_media_type("/path/to/file.png") == 'image'
        assert provider._detect_media_type("/path/to/file.gif") == 'image'
        assert provider._detect_media_type("/path/to/file.webp") == 'image'

    @patch('os.path.exists')
    def test_detect_media_type_video(self, mock_exists):
        """Test media type detection for videos."""
        mock_exists.return_value = True

        provider = LinkedInProvider(access_token="test_token")

        # Test various video extensions
        assert provider._detect_media_type("/path/to/file.mp4") == 'video'
        assert provider._detect_media_type("/path/to/file.mov") == 'video'
        assert provider._detect_media_type("/path/to/file.avi") == 'video'
        assert provider._detect_media_type("/path/to/file.webm") == 'video'

    @patch('mimetypes.guess_type')
    @patch('os.path.exists')
    def test_detect_media_type_unsupported(self, mock_exists, mock_guess_type):
        """Test media type detection for unsupported files."""
        mock_exists.return_value = True
        mock_guess_type.return_value = ('text/plain', None)

        provider = LinkedInProvider(access_token="test_token")

        with pytest.raises(UploadError, match="Unsupported media type"):
            provider._detect_media_type("/path/to/file.txt")

        mock_guess_type.return_value = ('application/pdf', None)
        with pytest.raises(UploadError, match="Unsupported media type"):
            provider._detect_media_type("/path/to/file.pdf")

    def test_detect_media_type_file_not_found(self):
        """Test media type detection for non-existent file."""
        provider = LinkedInProvider(access_token="test_token")

        with pytest.raises(UploadError, match="File not found"):
            provider._detect_media_type("/path/to/nonexistent.jpg")

    @patch('os.path.exists')
    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    def test_upload_media_api_failure_raises_error(self, mock_client_post, mock_login, mock_exists):
        """Test media upload API failure raises UploadError."""
        mock_exists.return_value = True
        mock_client_post.side_effect = Exception("API error")

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        with pytest.raises(UploadError, match="Failed to upload media"):
            provider.upload_media("/path/to/image.jpg")

    @patch('mimetypes.guess_type')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('socialcli.providers.linkedin.provider.LinkedInProvider.login')
    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.post')
    @patch('builtins.open', create=True)
    @patch('requests.put')
    def test_upload_media_http_error(self, mock_put, mock_open, mock_client_post, mock_login, mock_getsize, mock_exists, mock_guess_type):
        """Test media upload HTTP error raises UploadError."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        mock_guess_type.return_value = ('image/jpeg', None)

        # Mock successful registration
        mock_register_response = Mock()
        mock_register_response.json.return_value = {
            'value': {
                'uploadMechanism': {
                    'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest': {
                        'uploadUrl': 'https://upload.linkedin.com/abc123'
                    }
                },
                'asset': 'urn:li:digitalmediaAsset:123456'
            }
        }
        mock_client_post.return_value = mock_register_response

        # Mock file upload failure
        mock_upload_response = Mock()
        mock_upload_response.raise_for_status.side_effect = requests.HTTPError("Upload failed")
        mock_put.return_value = mock_upload_response

        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        provider = LinkedInProvider(access_token="test_token")
        provider._person_urn = "urn:li:person:test_user"

        with pytest.raises(UploadError, match="Upload failed"):
            provider.upload_media("/path/to/image.jpg")


class TestLinkedInProviderGetProfile:
    """Test get profile functionality."""

    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.get')
    def test_get_profile_success(self, mock_client_get):
        """Test successful profile retrieval using OpenID Connect userinfo endpoint."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'sub': 'test_user_id',
            'name': 'John Doe',
            'given_name': 'John',
            'family_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        mock_client_get.return_value = mock_response

        provider = LinkedInProvider(access_token="test_token")
        result = provider.get_profile()

        # Verify backward compatibility: 'sub' is mapped to 'id'
        assert result['id'] == 'test_user_id'
        assert result['sub'] == 'test_user_id'
        mock_client_get.assert_called_once_with('userinfo', use_rest_api=False)

    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.get')
    def test_get_profile_failure_raises_error(self, mock_client_get):
        """Test profile retrieval failure raises AuthenticationError."""
        mock_client_get.side_effect = requests.HTTPError("API error")

        provider = LinkedInProvider(access_token="test_token")

        with pytest.raises(AuthenticationError, match="Failed to get profile"):
            provider.get_profile()

    @patch('socialcli.providers.linkedin.client.LinkedInAPIClient.get')
    def test_get_profile_without_token_raises_error(self, mock_client_get):
        """Test profile retrieval without token raises AuthenticationError."""
        mock_client_get.side_effect = AuthenticationError("No token")

        provider = LinkedInProvider(access_token="test_token")

        with pytest.raises(AuthenticationError):
            provider.get_profile()
