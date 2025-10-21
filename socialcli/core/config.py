"""Configuration management for SocialCLI.

Handles loading and managing configuration from YAML files,
including provider credentials, tokens, and user preferences.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """Configuration for a social media provider."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[str] = None


@dataclass
class Config:
    """Main configuration for SocialCLI."""
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    default_provider: str = "linkedin"
    config_path: Optional[Path] = None

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'Config':
        """Load configuration from YAML file.

        Args:
            config_path: Path to config file. Defaults to ~/.socialcli/config.yaml

        Returns:
            Config instance
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

        return cls(
            providers=providers,
            default_provider=data.get('default_provider', 'linkedin'),
            config_path=config_path
        )

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
