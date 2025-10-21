"""LinkedIn OAuth 2.0 authentication.

Handles the OAuth 2.0 three-legged authentication flow for LinkedIn.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode
from socialcli.core.config import Config


class LinkedInAuth:
    """Manages LinkedIn OAuth 2.0 authentication flow."""

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/callback",
        config: Optional[Config] = None
    ):
        """Initialize LinkedIn OAuth handler.

        Args:
            client_id: LinkedIn application client ID
            client_secret: LinkedIn application client secret
            redirect_uri: OAuth callback URI
            config: Config instance for token storage (optional)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.config = config or Config()

    def get_authorization_url(self, scope: Optional[str] = None) -> str:
        """Generate OAuth authorization URL.

        Args:
            scope: Space-separated OAuth scopes. Defaults to standard scopes.

        Returns:
            Authorization URL for user to visit
        """
        if scope is None:
            # Updated scopes for LinkedIn API v2 (OpenID Connect + Sign In with LinkedIn)
            # These scopes work with unverified apps during development
            scope = "openid profile email w_member_social"

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': scope,
        }

        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dict containing access_token, expires_in, and optionally refresh_token

        Raises:
            requests.HTTPError: If token exchange fails
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict containing new access_token and expires_in

        Raises:
            requests.HTTPError: If token refresh fails
        """
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        return response.json()

    def save_tokens(self, token_data: Dict[str, Any]) -> None:
        """Save access and refresh tokens to config.

        Args:
            token_data: Dict containing access_token, expires_in, and optionally refresh_token
        """
        # Calculate expiration timestamp
        expires_in = token_data.get('expires_in', 5184000)  # Default 60 days
        token_expiry = (datetime.now() + timedelta(seconds=expires_in)).isoformat()

        # Get existing provider config or create new one
        provider_config = self.config.get_provider_config('linkedin')
        if provider_config is None:
            from socialcli.core.config import ProviderConfig
            provider_config = ProviderConfig()

        # Update tokens
        provider_config.access_token = token_data['access_token']
        provider_config.token_expiry = token_expiry

        # Save refresh token if provided
        if 'refresh_token' in token_data:
            provider_config.refresh_token = token_data['refresh_token']

        self.config.set_provider_config('linkedin', provider_config)
        self.config.save()

    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token or None if authentication needed

        Raises:
            requests.HTTPError: If token refresh fails
        """
        provider_config = self.config.get_provider_config('linkedin')
        if not provider_config:
            return None

        access_token = provider_config.access_token
        token_expiry = provider_config.token_expiry
        refresh_token = provider_config.refresh_token

        # Check if token exists
        if not access_token:
            return None

        # Check if token is expired or will expire soon (within 5 minutes)
        if token_expiry:
            expiry = datetime.fromisoformat(token_expiry)
            if datetime.now() >= expiry - timedelta(minutes=5):
                # Token expired or expiring soon, try to refresh
                if refresh_token:
                    try:
                        new_token_data = self.refresh_access_token(refresh_token)
                        self.save_tokens(new_token_data)
                        return new_token_data['access_token']
                    except requests.HTTPError:
                        # Refresh failed, return None to trigger re-authentication
                        return None
                else:
                    # No refresh token, need re-authentication
                    return None

        return access_token

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid token.

        Returns:
            True if authenticated with valid token, False otherwise
        """
        return self.get_valid_token() is not None

    def clear_tokens(self) -> None:
        """Clear stored tokens from config."""
        provider_config = self.config.get_provider_config('linkedin')
        if provider_config:
            provider_config.access_token = None
            provider_config.refresh_token = None
            provider_config.token_expiry = None

            self.config.set_provider_config('linkedin', provider_config)
            self.config.save()
