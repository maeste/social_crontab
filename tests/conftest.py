"""Shared test fixtures and configuration."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory with valid config."""
    config_dir = tmp_path / ".socialcli"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create a valid config file
    config_file = config_dir / "config.yaml"
    config_data = {
        'providers': {
            'linkedin': {
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret',
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token'
            }
        }
    }

    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    return config_dir


@pytest.fixture
def mock_home(temp_config_dir, monkeypatch):
    """Mock Path.home() to return temp directory."""
    monkeypatch.setattr(Path, 'home', lambda: temp_config_dir.parent)
    return temp_config_dir.parent


@pytest.fixture
def sample_post_file(tmp_path):
    """Create a sample post file."""
    post_file = tmp_path / "test_post.md"
    post_file.write_text("""---
platform: linkedin
visibility: public
---

This is a test post.
""")
    return post_file


@pytest.fixture
def mock_linkedin_auth():
    """Create a mock LinkedIn auth object."""
    auth = Mock()
    auth.is_authenticated.return_value = True
    auth.get_authorization_url.return_value = "https://linkedin.com/oauth/authorize"
    auth.exchange_code_for_token.return_value = {
        'access_token': 'test_token',
        'expires_in': 3600
    }
    return auth


@pytest.fixture
def mock_linkedin_provider():
    """Create a mock LinkedIn provider object."""
    provider = Mock()
    provider.get_profile.return_value = {
        'localizedFirstName': 'Test',
        'localizedLastName': 'User'
    }
    provider.post.return_value = {
        'id': 'urn:li:share:123',
        'url': 'https://linkedin.com/posts/123'
    }
    provider.comment.return_value = {
        'id': 'urn:li:comment:456'
    }
    return provider
