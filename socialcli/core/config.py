"""Configuration management for SocialCLI.

Handles loading and managing configuration from YAML files,
including provider credentials, tokens, and user preferences.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class ProviderConfig:
    """Configuration for a social media provider."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[str] = None

    def validate(self, provider_name: str) -> List[str]:
        """Validate provider configuration.

        Args:
            provider_name: Name of the provider for error messages

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check required fields for authentication
        if not self.client_id:
            errors.append(f"{provider_name}: missing required field 'client_id'")
        if not self.client_secret:
            errors.append(f"{provider_name}: missing required field 'client_secret'")

        # Note: access_token and refresh_token are optional during initial setup
        # They will be populated after OAuth flow

        return errors

    def is_authenticated(self) -> bool:
        """Check if provider has valid authentication tokens.

        Returns:
            True if access_token is present
        """
        return bool(self.access_token)


@dataclass
class Config:
    """Main configuration for SocialCLI."""
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    default_provider: str = "linkedin"
    config_path: Optional[Path] = None

    @classmethod
    def load(cls, config_path: Optional[Path] = None, validate: bool = True) -> 'Config':
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file. Defaults to ~/.socialcli/config.yaml
            validate: Whether to validate configuration on load

        Returns:
            Config instance

        Raises:
            ConfigValidationError: If validation fails and validate=True
        """
        if config_path is None:
            config_path = Path.home() / '.socialcli' / 'config.yaml'

        if not config_path.exists():
            # Create default config
            config = cls(config_path=config_path)
            config.save()
            return config

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}

        providers = {}
        for name, provider_data in data.get('providers', {}).items():
            providers[name] = ProviderConfig(**provider_data)

        config = cls(
            providers=providers,
            default_provider=data.get('default_provider', 'linkedin'),
            config_path=config_path
        )

        if validate:
            config.validate()

        return config

    def save(self):
        """Save configuration to YAML file."""
        if self.config_path is None:
            self.config_path = Path.home() / '.socialcli' / 'config.yaml'

        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'default_provider': self.default_provider,
            'providers': {}
        }

        for name, provider_config in self.providers.items():
            data['providers'][name] = {
                'client_id': provider_config.client_id,
                'client_secret': provider_config.client_secret,
                'access_token': provider_config.access_token,
                'refresh_token': provider_config.refresh_token,
                'token_expiry': provider_config.token_expiry,
            }

        with open(self.config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def validate(self):
        """Validate the entire configuration.

        Raises:
            ConfigValidationError: If validation fails
        """
        errors = []

        # Validate default provider exists
        if self.default_provider and self.default_provider not in self.providers:
            errors.append(
                f"Default provider '{self.default_provider}' is not configured. "
                f"Available providers: {list(self.providers.keys())}"
            )

        # Validate each provider configuration
        for provider_name, provider_config in self.providers.items():
            provider_errors = provider_config.validate(provider_name)
            errors.extend(provider_errors)

        if errors:
            raise ConfigValidationError(
                "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            )

    def get_provider_config(self, provider_name: Optional[str] = None) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider.

        Args:
            provider_name: Name of the provider. Uses default if None.

        Returns:
            ProviderConfig or None if not found
        """
        if provider_name is None:
            provider_name = self.default_provider

        return self.providers.get(provider_name)

    def set_provider_config(self, provider_name: str, config: ProviderConfig):
        """Set configuration for a provider.

        Args:
            provider_name: Name of the provider
            config: Provider configuration
        """
        self.providers[provider_name] = config
        self.save()

    def update_tokens(
        self,
        provider_name: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[str] = None
    ):
        """Update tokens for a provider.

        Args:
            provider_name: Name of the provider
            access_token: New access token
            refresh_token: New refresh token (optional)
            token_expiry: Token expiration time (optional)
        """
        provider_config = self.providers.get(provider_name)
        if provider_config is None:
            provider_config = ProviderConfig()
            self.providers[provider_name] = provider_config

        provider_config.access_token = access_token
        if refresh_token:
            provider_config.refresh_token = refresh_token
        if token_expiry:
            provider_config.token_expiry = token_expiry

        self.save()
