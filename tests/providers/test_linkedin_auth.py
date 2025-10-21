"""Tests for LinkedIn OAuth 2.0 authentication."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from socialcli.providers.linkedin.auth import LinkedInAuth
from socialcli.core.config import Config, ProviderConfig


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config for testing."""
    config_file = tmp_path / "config.yaml"
    return Config(config_path=config_file)


@pytest.fixture
def auth_handler(temp_config):
    """Create a LinkedIn auth handler with test credentials."""
    return LinkedInAuth(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8080/callback",
        config=temp_config
    )


class TestLinkedInAuthInitialization:
    """Test LinkedInAuth initialization."""

    def test_init_with_credentials(self, temp_config):
        """Test initializing auth handler with credentials."""
        auth = LinkedInAuth(
            client_id="test_id",
            client_secret="test_secret",
            config=temp_config
        )

        assert auth.client_id == "test_id"
        assert auth.client_secret == "test_secret"
        assert auth.redirect_uri == "http://localhost:8080/callback"
        assert auth.config is not None

    def test_init_with_custom_redirect_uri(self, temp_config):
        """Test initializing with custom redirect URI."""
        auth = LinkedInAuth(
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="https://example.com/callback",
            config=temp_config
        )

        assert auth.redirect_uri == "https://example.com/callback"


class TestAuthorizationURL:
    """Test OAuth authorization URL generation."""

    def test_get_authorization_url_default_scopes(self, auth_handler):
        """Test generating authorization URL with default scopes."""
        url = auth_handler.get_authorization_url()

        assert "https://www.linkedin.com/oauth/v2/authorization" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http" in url
        assert "w_member_social" in url
        assert "r_liteprofile" in url
        assert "response_type=code" in url

    def test_get_authorization_url_custom_scopes(self, auth_handler):
        """Test generating authorization URL with custom scopes."""
        url = auth_handler.get_authorization_url(scope="custom_scope another_scope")

        assert "custom_scope" in url
        assert "another_scope" in url

    def test_authorization_url_includes_all_params(self, auth_handler):
        """Test that authorization URL includes all required parameters."""
        url = auth_handler.get_authorization_url()

        assert "response_type=" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
        assert "scope=" in url


class TestTokenExchange:
    """Test authorization code exchange for access token."""

    @patch('socialcli.providers.linkedin.auth.requests.post')
    def test_exchange_code_for_token_success(self, mock_post, auth_handler):
        """Test successful code exchange."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 5184000,
            'refresh_token': 'test_refresh_token'
        }
        mock_post.return_value = mock_response

        result = auth_handler.exchange_code_for_token('auth_code_123')

        assert result['access_token'] == 'test_access_token'
        assert result['expires_in'] == 5184000
        assert result['refresh_token'] == 'test_refresh_token'

        # Verify correct API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://www.linkedin.com/oauth/v2/accessToken"
        assert call_args[1]['data']['grant_type'] == 'authorization_code'
        assert call_args[1]['data']['code'] == 'auth_code_123'

    @patch('socialcli.providers.linkedin.auth.requests.post')
    def test_exchange_code_for_token_failure(self, mock_post, auth_handler):
        """Test failed code exchange."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            auth_handler.exchange_code_for_token('invalid_code')


class TestTokenRefresh:
    """Test token refresh functionality."""

    @patch('socialcli.providers.linkedin.auth.requests.post')
    def test_refresh_access_token_success(self, mock_post, auth_handler):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'expires_in': 5184000
        }
        mock_post.return_value = mock_response

        result = auth_handler.refresh_access_token('refresh_token_123')

        assert result['access_token'] == 'new_access_token'
        assert result['expires_in'] == 5184000

        # Verify correct API call
        call_args = mock_post.call_args
        assert call_args[1]['data']['grant_type'] == 'refresh_token'
        assert call_args[1]['data']['refresh_token'] == 'refresh_token_123'

    @patch('socialcli.providers.linkedin.auth.requests.post')
    def test_refresh_access_token_failure(self, mock_post, auth_handler):
        """Test failed token refresh."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response

        with pytest.raises(Exception):
            auth_handler.refresh_access_token('invalid_refresh_token')


class TestTokenStorage:
    """Test token storage in config."""

    def test_save_tokens(self, auth_handler):
        """Test saving tokens to config."""
        token_data = {
            'access_token': 'test_token',
            'expires_in': 3600,
            'refresh_token': 'test_refresh'
        }

        auth_handler.save_tokens(token_data)

        # Verify tokens were saved
        provider_config = auth_handler.config.get_provider_config('linkedin')
        assert provider_config.access_token == 'test_token'
        assert provider_config.refresh_token == 'test_refresh'
        assert provider_config.token_expiry is not None

    def test_save_tokens_without_refresh_token(self, auth_handler):
        """Test saving tokens without refresh token."""
        token_data = {
            'access_token': 'test_token',
            'expires_in': 3600
        }

        auth_handler.save_tokens(token_data)

        provider_config = auth_handler.config.get_provider_config('linkedin')
        assert provider_config.access_token == 'test_token'
        assert provider_config.refresh_token is None

    def test_save_tokens_calculates_expiry(self, auth_handler):
        """Test that save_tokens correctly calculates expiry timestamp."""
        token_data = {
            'access_token': 'test_token',
            'expires_in': 3600  # 1 hour
        }

        before_save = datetime.now()
        auth_handler.save_tokens(token_data)
        after_save = datetime.now()

        provider_config = auth_handler.config.get_provider_config('linkedin')
        token_expiry = datetime.fromisoformat(provider_config.token_expiry)

        # Should be approximately 1 hour from now
        expected_expiry = before_save + timedelta(seconds=3600)
        assert abs((token_expiry - expected_expiry).total_seconds()) < 5


class TestGetValidToken:
    """Test getting valid access token with automatic refresh."""

    def test_get_valid_token_when_no_token(self, auth_handler):
        """Test getting token when none exists."""
        token = auth_handler.get_valid_token()
        assert token is None

    def test_get_valid_token_when_valid(self, auth_handler):
        """Test getting token when it's still valid."""
        # Save a token that expires in the future
        token_data = {
            'access_token': 'valid_token',
            'expires_in': 3600  # 1 hour
        }
        auth_handler.save_tokens(token_data)

        token = auth_handler.get_valid_token()
        assert token == 'valid_token'

    @patch('socialcli.providers.linkedin.auth.requests.post')
    def test_get_valid_token_when_expired_with_refresh(self, mock_post, auth_handler):
        """Test automatic refresh when token is expired."""
        # Save an expired token with refresh token
        expired_time = datetime.now() - timedelta(hours=1)
        provider_config = ProviderConfig(
            access_token='expired_token',
            token_expiry=expired_time.isoformat(),
            refresh_token='refresh_token_123'
        )
        auth_handler.config.set_provider_config('linkedin', provider_config)
        auth_handler.config.save()

        # Mock the refresh response
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'refreshed_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response

        token = auth_handler.get_valid_token()

        assert token == 'refreshed_token'
        # Verify refresh was called
        mock_post.assert_called_once()

    def test_get_valid_token_when_expired_without_refresh(self, auth_handler):
        """Test when token is expired and no refresh token available."""
        # Save an expired token without refresh token
        expired_time = datetime.now() - timedelta(hours=1)
        provider_config = ProviderConfig(
            access_token='expired_token',
            token_expiry=expired_time.isoformat()
        )
        auth_handler.config.set_provider_config('linkedin', provider_config)
        auth_handler.config.save()

        token = auth_handler.get_valid_token()
        assert token is None


class TestIsAuthenticated:
    """Test authentication status check."""

    def test_is_authenticated_when_no_token(self, auth_handler):
        """Test authentication status when no token exists."""
        assert auth_handler.is_authenticated() is False

    def test_is_authenticated_when_valid_token(self, auth_handler):
        """Test authentication status with valid token."""
        token_data = {
            'access_token': 'valid_token',
            'expires_in': 3600
        }
        auth_handler.save_tokens(token_data)

        assert auth_handler.is_authenticated() is True

    def test_is_authenticated_when_expired_token(self, auth_handler):
        """Test authentication status with expired token and no refresh."""
        expired_time = datetime.now() - timedelta(hours=1)
        provider_config = ProviderConfig(
            access_token='expired_token',
            token_expiry=expired_time.isoformat()
        )
        auth_handler.config.set_provider_config('linkedin', provider_config)
        auth_handler.config.save()

        assert auth_handler.is_authenticated() is False


class TestClearTokens:
    """Test token clearing functionality."""

    def test_clear_tokens(self, auth_handler):
        """Test clearing stored tokens."""
        # First save some tokens
        token_data = {
            'access_token': 'test_token',
            'expires_in': 3600,
            'refresh_token': 'test_refresh'
        }
        auth_handler.save_tokens(token_data)

        # Verify tokens exist
        provider_config = auth_handler.config.get_provider_config('linkedin')
        assert provider_config.access_token is not None

        # Clear tokens
        auth_handler.clear_tokens()

        # Verify tokens are gone
        provider_config = auth_handler.config.get_provider_config('linkedin')
        assert provider_config.access_token is None
        assert provider_config.refresh_token is None
        assert provider_config.token_expiry is None


class TestOAuthScopes:
    """Test OAuth scope handling."""

    def test_default_scopes_include_required(self, auth_handler):
        """Test that default scopes include required LinkedIn scopes."""
        url = auth_handler.get_authorization_url()

        # Required scopes from spec
        assert "w_member_social" in url
        assert "r_liteprofile" in url

    def test_custom_scopes_override_default(self, auth_handler):
        """Test that custom scopes override defaults."""
        url = auth_handler.get_authorization_url(scope="custom_scope")

        assert "custom_scope" in url
        # Should not contain default scopes
        assert "w_member_social" not in url
