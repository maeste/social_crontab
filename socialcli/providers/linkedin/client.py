"""LinkedIn API HTTP client.

Handles HTTP communication with LinkedIn REST API including authentication,
rate limiting, error handling, and retry logic.
"""

from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from socialcli.providers.base import AuthenticationError


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds (default 60 seconds)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: list[float] = []

    def wait_if_needed(self) -> None:
        """Block if rate limit would be exceeded."""
        now = time.time()

        # Remove requests older than time window
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < self.time_window]

        # Check if we've hit the limit
        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = self.requests[0]
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                time.sleep(wait_time)
                # Clean up old requests after waiting
                now = time.time()
                self.requests = [req_time for req_time in self.requests
                               if now - req_time < self.time_window]

        # Record this request
        self.requests.append(time.time())


class LinkedInAPIClient:
    """HTTP client for LinkedIn REST API.

    Handles authentication, rate limiting, retries, and error handling
    for all API communication.
    """

    API_BASE = "https://api.linkedin.com/v2"
    API_REST_BASE = "https://api.linkedin.com/v2"

    # LinkedIn rate limits (conservative defaults)
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    DEFAULT_TIME_WINDOW = 60  # seconds

    def __init__(
        self,
        access_token: Optional[str] = None,
        rate_limit: int = DEFAULT_RATE_LIMIT,
        time_window: int = DEFAULT_TIME_WINDOW,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """Initialize LinkedIn API client.

        Args:
            access_token: OAuth access token for authentication
            rate_limit: Maximum requests per time window (default 100)
            time_window: Rate limit time window in seconds (default 60)
            max_retries: Maximum retry attempts for failed requests (default 3)
            backoff_factor: Exponential backoff factor for retries (default 0.3)
        """
        self.access_token = access_token
        self.rate_limiter = RateLimiter(rate_limit, time_window)

        # Configure session with retry strategy
        self.session = requests.Session()

        # Retry on specific status codes and connection errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers with authentication.

        Args:
            additional_headers: Optional additional headers to include

        Returns:
            Dict of HTTP headers

        Raises:
            AuthenticationError: If access token not set
        """
        if not self.access_token:
            raise AuthenticationError("Access token not set. Please authenticate first.")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202504'
        }

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle API error responses with detailed error messages.

        Args:
            response: HTTP response object

        Raises:
            AuthenticationError: For 401 Unauthorized
            requests.HTTPError: For other HTTP errors with enhanced message
        """
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Token may be expired or invalid."
            )

        try:
            error_data = response.json()
            error_message = error_data.get('message', response.text)
            service_error = error_data.get('serviceErrorCode', '')

            detailed_message = (
                f"LinkedIn API error (HTTP {response.status_code}): {error_message}"
            )
            if service_error:
                detailed_message += f" [Service Error Code: {service_error}]"

        except ValueError:
            # Response is not JSON
            detailed_message = (
                f"LinkedIn API error (HTTP {response.status_code}): {response.text}"
            )

        # Raise HTTPError with detailed message
        raise requests.HTTPError(detailed_message, response=response)

    def request(
        self,
        method: str,
        endpoint: str,
        use_rest_api: bool = False,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[bytes, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request to LinkedIn API with rate limiting and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            use_rest_api: Use REST API base URL instead of v2 (default False)
            json: JSON payload for request body
            data: Raw data for request body
            headers: Additional headers to include
            params: Query parameters
            **kwargs: Additional arguments passed to requests

        Returns:
            HTTP response object

        Raises:
            AuthenticationError: If authentication fails
            requests.HTTPError: If request fails after retries
        """
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        # Build full URL
        base_url = self.API_REST_BASE if use_rest_api else self.API_BASE
        url = f"{base_url}/{endpoint.lstrip('/')}"

        # Build headers
        request_headers = self._get_headers(headers)

        # Make request
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                data=data,
                headers=request_headers,
                params=params,
                **kwargs
            )

            # Handle errors
            if not response.ok:
                self._handle_error_response(response)

            return response

        except requests.exceptions.RetryError as e:
            raise requests.HTTPError(
                f"Request failed after maximum retries: {str(e)}"
            )
        except requests.exceptions.RequestException as e:
            raise requests.HTTPError(
                f"Request failed: {str(e)}"
            )

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to request()

        Returns:
            HTTP response object
        """
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to request()

        Returns:
            HTTP response object
        """
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to request()

        Returns:
            HTTP response object
        """
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to request()

        Returns:
            HTTP response object
        """
        return self.request("DELETE", endpoint, **kwargs)

    def set_access_token(self, access_token: str) -> None:
        """Update access token.

        Args:
            access_token: New OAuth access token
        """
        self.access_token = access_token

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
