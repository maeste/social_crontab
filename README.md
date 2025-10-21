# SocialCLI – CLI Framework for Social Scheduling

**Version:** 0.1.0
**Author:** Stefano Maestri
**License:** Apache License 2.0

A command-line framework for posting, commenting, and scheduling content across multiple social platforms (LinkedIn, X, Threads, Bluesky, Mastodon, etc.).

## Features

- 🔌 **Modular Provider System** - Extensible architecture for multiple social platforms
- 📅 **Scheduling** - Queue posts for future publication with local scheduler
- 🔐 **OAuth 2.0 Support** - Secure authentication with token management
- 📝 **Markdown Posts** - Write posts in Markdown with optional YAML front matter
- 🖼️ **Media Upload** - Upload images and media to social platforms
- 💾 **Local Storage** - SQLite-based queue and local file storage
- 🔄 **Cross-Platform** - Single tool for managing multiple social accounts

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/socialcli.git
cd socialcli

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Configuration

1. Create configuration directory:
```bash
mkdir -p ~/.socialcli
```

2. Create `~/.socialcli/config.yaml`:
```yaml
providers:
  linkedin:
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET
    access_token: YOUR_ACCESS_TOKEN
    refresh_token: YOUR_REFRESH_TOKEN

default_provider: linkedin
```

### Basic Usage

```bash
# Authenticate with LinkedIn
socialcli login --provider linkedin

# Post from a markdown file
socialcli post --file post.md --provider linkedin

# Add a comment to a post
socialcli comment --provider linkedin --target-id POST_ID --text "Great post!"

# List scheduled posts
socialcli queue --list
```

## Post File Format

### Simple Text Post

```markdown
💬 Agents, AI, and Humility

Karpathy's latest interview sparks an important point: tools evolve, but humility must remain.

#AI #AgenticAI
```

### Post with Front Matter

```markdown
---
title: Karpathy and Developers' Humility
tags: [AI, Agents]
provider: linkedin
schedule: 2025-10-21T09:00
---

💬 Agents, AI, and Humility

Karpathy's latest interview sparks an important point: tools evolve, but humility must remain.

#AI #AgenticAI
```

## Project Structure

```
socialcli/
├── core/                    # Core framework functionality
│   ├── cli.py              # CLI entry point and command handlers
│   ├── scheduler.py        # Local scheduler with SQLite
│   ├── storage.py          # Storage and logging management
│   └── config.py           # Configuration (tokens, profiles)
├── providers/              # Provider abstraction layer
│   ├── base.py             # SocialProvider ABC
│   └── linkedin/           # LinkedIn provider (MVP)
│       ├── provider.py     # LinkedInProvider implementation
│       └── auth.py         # OAuth 2.0 authentication
└── utils/                  # Shared utilities
    └── parser.py           # Post file parser

tests/                      # Test suite
├── core/
├── providers/
│   └── linkedin/
└── utils/
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=socialcli tests/

# Format code
black socialcli/ tests/

# Lint code
flake8 socialcli/ tests/

# Type checking
mypy socialcli/
```

### Adding a New Provider

1. Create a new directory under `socialcli/providers/`
2. Implement the `SocialProvider` abstract base class
3. Add authentication handler if needed
4. Register the provider in the CLI

Example:
```python
from socialcli.providers.base import SocialProvider

class XProvider(SocialProvider):
    def login(self) -> bool:
        # Implement OAuth flow
        pass

    def post(self, content: str, **kwargs):
        # Implement posting logic
        pass

    # ... implement other methods
```

## LinkedIn Provider

The LinkedIn provider is the reference implementation and supports:

- OAuth 2.0 3-legged authentication
- Text posts and posts with images
- Comments and reshares
- Media upload via LinkedIn API
- Token refresh and management

### LinkedIn API Scopes

Required scopes:
- `w_member_social` - Create posts
- `r_liteprofile` - Read profile information

For organization posts:
- `w_organization_social` - Create organization posts
- `rw_organization_admin` - Manage organization

### Getting LinkedIn Credentials

1. Create an app at https://www.linkedin.com/developers/
2. Configure OAuth 2.0 settings
3. Add redirect URI: `http://localhost:8080/callback`
4. Copy Client ID and Client Secret to config

## Configuration Reference

### Config File Location

Default: `~/.socialcli/config.yaml`

### Configuration Schema

```yaml
providers:
  linkedin:
    client_id: string       # LinkedIn app client ID
    client_secret: string   # LinkedIn app client secret
    access_token: string    # OAuth access token
    refresh_token: string   # OAuth refresh token (optional)
    token_expiry: string    # Token expiration time (optional)

  # Add more providers as needed
  x:
    # X provider config

default_provider: linkedin  # Default provider if not specified
```

### Environment Variables

Copy `.env.example` to `~/.socialcli/.env`:

```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_REFRESH_TOKEN=your_refresh_token
DEFAULT_PROVIDER=linkedin
```

## Scheduler

The scheduler uses SQLite to queue posts for future publication.

### Database Schema

```sql
CREATE TABLE scheduled_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    author TEXT NOT NULL,
    file_path TEXT NOT NULL,
    publish_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Database Location

Default: `~/.socialcli/scheduler.db`

## Roadmap

| Phase | Goal | Status |
|-------|------|--------|
| 1️⃣ | MVP LinkedIn | ✅ In Progress |
| 2️⃣ | Plugin system | 📋 Planned |
| 3️⃣ | X and Bluesky | 📋 Planned |
| 4️⃣ | Web dashboard | 📋 Future |
| 5️⃣ | Notion / Git integration | 📋 Future |

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/socialcli/issues
- Documentation: See `docs/` directory

## Acknowledgments

Inspired by the need for a unified, open-source CLI tool for social media management.

---

> "Start with LinkedIn. Scale to the social web." 🌍
