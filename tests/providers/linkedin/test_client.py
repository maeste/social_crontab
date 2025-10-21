"""Tests for LinkedIn API client."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import RetryError, RequestException

from socialcli.providers.linkedin.client import LinkedInAPIClient, RateLimiter
from socialcli.providers.base import AuthenticationError


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes with correct defaults."""
        limiter = RateLimiter(max_requests=10, time_window=60)
        assert limiter.max_requests == 10
        assert limiter.time_window == 60
        assert limiter.requests == []

    def test_rate_limiter_allows_requests_under_limit(self):
        """Test rate limiter allows requests under the limit."""
        limiter = RateLimiter(max_requests=5, time_window=60)

        # Should not block for requests under limit
        for _ in range(5):
            start = time.time()
            limiter.wait_if_needed()
            duration = time.time() - start
            assert duration < 0.1  # Should be nearly instant

    def test_rate_limiter_blocks_when_limit_exceeded(self):
        """Test rate limiter blocks when limit is exceeded."""
        limiter = RateLimiter(max_requests=3, time_window=1)

        # Make 3 requests quickly
        for _ in range(3):
            limiter.wait_if_needed()

        # 4th request should block
        start = time.time()
        limiter.wait_if_needed()
        duration = time.time() - start

        # Should have waited approximately 1 second
        assert duration >= 0.9
        assert duration < 1.5

    def test_rate_limiter_cleans_old_requests(self):
        """Test rate limiter removes old requests from tracking."""
        limiter = RateLimiter(max_requests=2, time_window=1)

        # Make 2 requests
        limiter.wait_if_needed()
        limiter.wait_if_needed()

        # Wait for time window to pass
        time.sleep(1.1)

        # Should be able to make 2 more requests without blocking
        start = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        duration = time.time() - start

        assert duration < 0.2  # Should be nearly instant


class TestLinkedInAPIClient:
    """Test LinkedIn API client."""

    @pytest.fixture
    def client(self):
        """Create API client with access token."""
        return LinkedInAPIClient(access_token="test_token_123")

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=requests.Response)
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"id": "test123"}
        return response

    def test_client_initialization(self):
        """Test client initializes with correct defaults."""
        client = LinkedInAPIClient(access_token="test_token")

        assert client.access_token == "test_token"
        assert client.rate_limiter.max_requests == 100
        assert client.rate_limiter.time_window == 60
        assert isinstance(client.session, requests.Session)

    def test_client_initialization_custom_rate_limit(self):
        """Test client initialization with custom rate limit."""
        client = LinkedInAPIClient(
            access_token="test_token",
            rate_limit=50,
            time_window=30
        )

        assert client.rate_limiter.max_requests == 50
        assert client.rate_limiter.time_window == 30

    def test_get_headers_with_token(self, client):
        """Test headers include authentication."""
        headers = client._get_headers()

        assert headers['Authorization'] == 'Bearer test_token_123'
        assert headers['Content-Type'] == 'application/json'
        assert headers['X-Restli-Protocol-Version'] == '2.0.0'

    def test_get_headers_without_token(self):
        """Test headers raise error without token."""
        client = LinkedInAPIClient()

        with pytest.raises(AuthenticationError, match="Access token not set"):
            client._get_headers()

    def test_get_headers_with_additional_headers(self, client):
        """Test additional headers are merged."""
        headers = client._get_headers({'Custom-Header': 'value'})

        assert headers['Authorization'] == 'Bearer test_token_123'
        assert headers['Custom-Header'] == 'value'

    def test_handle_error_response_401(self, client):
        """Test 401 raises AuthenticationError."""
        response = Mock(spec=requests.Response)
        response.status_code = 401
        response.json.return_value = {"message": "Invalid token"}

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            client._handle_error_response(response)

    def test_handle_error_response_with_json_error(self, client):
        """Test error response with JSON error details."""
        response = Mock(spec=requests.Response)
        response.status_code = 400
        response.json.return_value = {
            "message": "Invalid request",
            "serviceErrorCode": 12345
        }
        response.text = "Bad Request"

        with pytest.raises(requests.HTTPError) as exc_info:
            client._handle_error_response(response)

        error_msg = str(exc_info.value)
        assert "Invalid request" in error_msg
        assert "12345" in error_msg
        assert "400" in error_msg

    def test_handle_error_response_non_json(self, client):
        """Test error response with non-JSON body."""
        response = Mock(spec=requests.Response)
        response.status_code = 500
        response.json.side_effect = ValueError("Not JSON")
        response.text = "Internal Server Error"

        with pytest.raises(requests.HTTPError) as exc_info:
            client._handle_error_response(response)

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal Server Error" in error_msg

    @patch.object(LinkedInAPIClient, '_get_headers')
    def test_request_get_success(self, mock_get_headers, client, mock_response):
        """Test successful GET request."""
        mock_get_headers.return_value = {'Authorization': 'Bearer test_token_123'}

        with patch.object(client.session, 'request', return_value=mock_response):
            response = client.request("GET", "/me")

            assert response.ok
            assert response.json() == {"id": "test123"}
            client.session.request.assert_called_once()

    @patch.object(LinkedInAPIClient, '_get_headers')
    def test_request_post_with_json(self, mock_get_headers, client, mock_response):
        """Test POST request with JSON payload."""
        mock_get_headers.return_value = {'Authorization': 'Bearer test_token_123'}
        post_data = {"text": "Hello LinkedIn"}

        with patch.object(client.session, 'request', return_value=mock_response):
            response = client.request("POST", "/ugcPosts", json=post_data)

            assert response.ok
            client.session.request.assert_called_once()
            call_kwargs = client.session.request.call_args[1]
            assert call_kwargs['json'] == post_data

    def test_request_uses_rate_limiter(self, client, mock_response):
        """Test request applies rate limiting."""
        with patch.object(client.rate_limiter, 'wait_if_needed') as mock_wait:
            with patch.object(client.session, 'request', return_value=mock_response):
                client.request("GET", "/me")

                mock_wait.assert_called_once()

    def test_request_uses_rest_api_base(self, client, mock_response):
        """Test request can use REST API base URL."""
        with patch.object(client.session, 'request', return_value=mock_response) as mock_req:
            client.request("POST", "/posts", use_rest_api=True)

            call_args = mock_req.call_args
            assert call_args[1]['url'].startswith(client.API_REST_BASE)

    def test_request_uses_v2_api_base_by_default(self, client, mock_response):
        """Test request uses v2 API base by default."""
        with patch.object(client.session, 'request', return_value=mock_response) as mock_req:
            client.request("GET", "/me")

            call_args = mock_req.call_args
            assert call_args[1]['url'].startswith(client.API_BASE)

    def test_request_handles_retry_error(self, client):
        """Test request handles retry exhaustion."""
        with patch.object(client.session, 'request', side_effect=RetryError("Max retries")):
            with pytest.raises(requests.HTTPError, match="failed after maximum retries"):
                client.request("GET", "/me")

    def test_request_handles_request_exception(self, client):
        """Test request handles general request exceptions."""
        with patch.object(client.session, 'request', side_effect=RequestException("Network error")):
            with pytest.raises(requests.HTTPError, match="Request failed"):
                client.request("GET", "/me")

    def test_get_method(self, client, mock_response):
        """Test GET convenience method."""
        with patch.object(client, 'request', return_value=mock_response) as mock_request:
            response = client.get("/me")

            mock_request.assert_called_once_with("GET", "/me")
            assert response == mock_response

    def test_post_method(self, client, mock_response):
        """Test POST convenience method."""
        with patch.object(client, 'request', return_value=mock_response) as mock_request:
            response = client.post("/ugcPosts", json={"text": "Hello"})

            mock_request.assert_called_once_with("POST", "/ugcPosts", json={"text": "Hello"})
            assert response == mock_response

    def test_put_method(self, client, mock_response):
        """Test PUT convenience method."""
        with patch.object(client, 'request', return_value=mock_response) as mock_request:
            response = client.put("/resource/123")

            mock_request.assert_called_once_with("PUT", "/resource/123")
            assert response == mock_response

    def test_delete_method(self, client, mock_response):
        """Test DELETE convenience method."""
        with patch.object(client, 'request', return_value=mock_response) as mock_request:
            response = client.delete("/resource/123")

            mock_request.assert_called_once_with("DELETE", "/resource/123")
            assert response == mock_response

    def test_set_access_token(self, client):
        """Test updating access token."""
        client.set_access_token("new_token_456")

        assert client.access_token == "new_token_456"

    def test_close_session(self, client):
        """Test closing HTTP session."""
        with patch.object(client.session, 'close') as mock_close:
            client.close()

            mock_close.assert_called_once()

    def test_context_manager(self):
        """Test client works as context manager."""
        with LinkedInAPIClient(access_token="test_token") as client:
            assert client.access_token == "test_token"

        # Session should be closed after context exit
        # (we can't easily test this without mocking)

    def test_retry_strategy_configured(self, client):
        """Test retry strategy is configured correctly."""
        adapter = client.session.get_adapter("https://")

        assert adapter.max_retries.total == 3
        assert adapter.max_retries.backoff_factor == 0.3
        assert 429 in adapter.max_retries.status_forcelist
        assert 500 in adapter.max_retries.status_forcelist
        assert 503 in adapter.max_retries.status_forcelist
