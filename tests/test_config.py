"""Tests for configuration management."""

import pytest
import tempfile
import yaml
from pathlib import Path

from socialcli.core.config import Config, ProviderConfig, ConfigValidationError


class TestProviderConfig:
    """Tests for ProviderConfig class."""

    def test_provider_config_creation(self):
        """Test creating a provider configuration."""
        config = ProviderConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.access_token == "test_access_token"
        assert config.refresh_token == "test_refresh_token"

    def test_validate_valid_config(self):
        """Test validation of valid provider configuration."""
        config = ProviderConfig(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        errors = config.validate("linkedin")
        assert len(errors) == 0

    def test_validate_missing_client_id(self):
        """Test validation fails when client_id is missing."""
        config = ProviderConfig(client_secret="test_client_secret")
        errors = config.validate("linkedin")
        assert len(errors) == 1
        assert "client_id" in errors[0]

    def test_validate_missing_client_secret(self):
        """Test validation fails when client_secret is missing."""
        config = ProviderConfig(client_id="test_client_id")
        errors = config.validate("linkedin")
        assert len(errors) == 1
        assert "client_secret" in errors[0]

    def test_validate_missing_both_credentials(self):
        """Test validation fails when both credentials are missing."""
        config = ProviderConfig()
        errors = config.validate("linkedin")
        assert len(errors) == 2
        assert any("client_id" in err for err in errors)
        assert any("client_secret" in err for err in errors)

    def test_is_authenticated_with_token(self):
        """Test is_authenticated returns True when access_token is present."""
        config = ProviderConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            access_token="test_access_token"
        )
        assert config.is_authenticated() is True

    def test_is_authenticated_without_token(self):
        """Test is_authenticated returns False when access_token is missing."""
        config = ProviderConfig(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        assert config.is_authenticated() is False


class TestConfig:
    """Tests for Config class."""

    def test_load_creates_default_config_if_missing(self, tmp_path):
        """Test that load creates a default config file if it doesn't exist."""
        config_path = tmp_path / "config.yaml"
        config = Config.load(config_path, validate=False)

        assert config_path.exists()
        assert config.default_provider == "linkedin"
        assert len(config.providers) == 0

    def test_load_existing_config(self, tmp_path):
        """Test loading an existing configuration file."""
        config_path = tmp_path / "config.yaml"
        config_data = {
            'default_provider': 'linkedin',
            'providers': {
                'linkedin': {
                    'client_id': 'test_id',
                    'client_secret': 'test_secret',
                    'access_token': 'test_token',
                    'refresh_token': 'test_refresh'
                }
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        config = Config.load(config_path, validate=False)

        assert config.default_provider == 'linkedin'
        assert 'linkedin' in config.providers
        assert config.providers['linkedin'].client_id == 'test_id'
        assert config.providers['linkedin'].client_secret == 'test_secret'
        assert config.providers['linkedin'].access_token == 'test_token'
        assert config.providers['linkedin'].refresh_token == 'test_refresh'

    def test_save_config(self, tmp_path):
        """Test saving configuration to file."""
        config_path = tmp_path / "config.yaml"

        provider_config = ProviderConfig(
            client_id='test_id',
            client_secret='test_secret',
            access_token='test_token'
        )

        config = Config(
            providers={'linkedin': provider_config},
            default_provider='linkedin',
            config_path=config_path
        )
        config.save()

        assert config_path.exists()

        with open(config_path, 'r') as f:
            saved_data = yaml.safe_load(f)

        assert saved_data['default_provider'] == 'linkedin'
        assert 'linkedin' in saved_data['providers']
        assert saved_data['providers']['linkedin']['client_id'] == 'test_id'

    def test_get_provider_config_default(self):
        """Test getting default provider configuration."""
        provider_config = ProviderConfig(client_id='test_id', client_secret='test_secret')
        config = Config(
            providers={'linkedin': provider_config},
            default_provider='linkedin'
        )

        result = config.get_provider_config()
        assert result == provider_config

    def test_get_provider_config_by_name(self):
        """Test getting provider configuration by name."""
        linkedin_config = ProviderConfig(client_id='linkedin_id', client_secret='linkedin_secret')
        twitter_config = ProviderConfig(client_id='twitter_id', client_secret='twitter_secret')

        config = Config(
            providers={
                'linkedin': linkedin_config,
                'twitter': twitter_config
            },
            default_provider='linkedin'
        )

        assert config.get_provider_config('twitter') == twitter_config
        assert config.get_provider_config('linkedin') == linkedin_config

    def test_get_provider_config_not_found(self):
        """Test getting non-existent provider configuration."""
        config = Config(providers={}, default_provider='linkedin')
        result = config.get_provider_config('nonexistent')
        assert result is None

    def test_set_provider_config(self, tmp_path):
        """Test setting provider configuration."""
        config_path = tmp_path / "config.yaml"
        config = Config(config_path=config_path)

        provider_config = ProviderConfig(
            client_id='new_id',
            client_secret='new_secret'
        )

        config.set_provider_config('linkedin', provider_config)

        assert 'linkedin' in config.providers
        assert config.providers['linkedin'] == provider_config
        assert config_path.exists()

    def test_update_tokens(self, tmp_path):
        """Test updating provider tokens."""
        config_path = tmp_path / "config.yaml"
        provider_config = ProviderConfig(
            client_id='test_id',
            client_secret='test_secret'
        )

        config = Config(
            providers={'linkedin': provider_config},
            config_path=config_path
        )

        config.update_tokens(
            'linkedin',
            access_token='new_access_token',
            refresh_token='new_refresh_token',
            token_expiry='2025-12-31T23:59:59'
        )

        updated_config = config.providers['linkedin']
        assert updated_config.access_token == 'new_access_token'
        assert updated_config.refresh_token == 'new_refresh_token'
        assert updated_config.token_expiry == '2025-12-31T23:59:59'

    def test_update_tokens_creates_provider_if_missing(self, tmp_path):
        """Test updating tokens for non-existent provider creates it."""
        config_path = tmp_path / "config.yaml"
        config = Config(config_path=config_path)

        config.update_tokens(
            'linkedin',
            access_token='new_access_token',
            refresh_token='new_refresh_token'
        )

        assert 'linkedin' in config.providers
        assert config.providers['linkedin'].access_token == 'new_access_token'

    def test_validate_valid_config(self, tmp_path):
        """Test validation succeeds for valid configuration."""
        config_path = tmp_path / "config.yaml"
        provider_config = ProviderConfig(
            client_id='test_id',
            client_secret='test_secret'
        )

        config = Config(
            providers={'linkedin': provider_config},
            default_provider='linkedin',
            config_path=config_path
        )

        # Should not raise
        config.validate()

    def test_validate_missing_default_provider(self):
        """Test validation fails when default provider is not configured."""
        config = Config(
            providers={'twitter': ProviderConfig(client_id='id', client_secret='secret')},
            default_provider='linkedin'
        )

        with pytest.raises(ConfigValidationError) as excinfo:
            config.validate()

        assert 'linkedin' in str(excinfo.value)
        assert 'not configured' in str(excinfo.value)

    def test_validate_provider_missing_credentials(self):
        """Test validation fails when provider is missing credentials."""
        config = Config(
            providers={'linkedin': ProviderConfig()},
            default_provider='linkedin'
        )

        with pytest.raises(ConfigValidationError) as excinfo:
            config.validate()

        assert 'client_id' in str(excinfo.value)
        assert 'client_secret' in str(excinfo.value)

    def test_load_with_validation_enabled(self, tmp_path):
        """Test loading config with validation enabled."""
        config_path = tmp_path / "config.yaml"
        config_data = {
            'default_provider': 'linkedin',
            'providers': {
                'linkedin': {
                    'client_id': 'test_id',
                    'client_secret': 'test_secret'
                }
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Should not raise
        config = Config.load(config_path, validate=True)
        assert config.default_provider == 'linkedin'

    def test_load_with_validation_fails_on_invalid_config(self, tmp_path):
        """Test loading config with validation fails on invalid config."""
        config_path = tmp_path / "config.yaml"
        config_data = {
            'default_provider': 'linkedin',
            'providers': {
                'linkedin': {
                    # Missing required fields
                }
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f)

        with pytest.raises(ConfigValidationError):
            Config.load(config_path, validate=True)

    def test_default_config_path(self, tmp_path, monkeypatch):
        """Test that default config path is ~/.socialcli/config.yaml."""
        # Mock Path.home() to return tmp_path
        def mock_home():
            return tmp_path

        monkeypatch.setattr(Path, 'home', mock_home)

        config = Config.load(validate=False)
        expected_path = tmp_path / '.socialcli' / 'config.yaml'

        assert config.config_path == expected_path
        assert expected_path.exists()
