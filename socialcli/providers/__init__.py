"""Social media provider abstraction layer.

This module defines the common interface that all social media providers
must implement, enabling a unified API for posting, commenting, and
interacting across different platforms.
"""

from socialcli.providers.base import SocialProvider

__all__ = ['SocialProvider']
