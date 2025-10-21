"""LinkedIn OAuth 2.0 authentication.

Handles the OAuth 2.0 three-legged authentication flow for LinkedIn.
"""

from typing import Optional, Dict, Any
import requests
from urllib.parse import urlencode


class LinkedInAuth:
    """Manages LinkedIn OAuth 2.0 authentication flow."""

    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/callback"
    ):
        """Initialize LinkedIn OAuth handler.

        Args:
            client_id: LinkedIn application client ID
            client_secret: LinkedIn application client secret
            redirect_uri: OAuth callback URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, scope: Optional[str] = None) -> str:
        """Generate OAuth authorization URL.

        Args:
            scope: Space-separated OAuth scopes. Defaults to standard scopes.

        Returns:
            Authorization URL for user to visit
        """
        if scope is None:
            scope = "w_member_social r_liteprofile"

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
