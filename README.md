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

# Schedule a post for later
socialcli post --file scheduled_post.md --schedule "2025-12-25T09:00:00"

# Add a comment to a post
socialcli comment --provider linkedin --target-id POST_ID --text "Great post!"

# List scheduled posts
socialcli queue --list

# Remove old completed posts from queue
socialcli prune --before 2025-01-01 --status completed
```

## Shell Completion

SocialCLI supports tab completion for Bash, Zsh, Fish, and PowerShell shells. Enable it to get command, option, and flag completions.

### Quick Setup

**Bash:**
```bash
socialcli completion bash > ~/.socialcli-completion.bash
echo 'source ~/.socialcli-completion.bash' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```zsh
socialcli completion zsh > ~/.socialcli-completion.zsh
echo 'source ~/.socialcli-completion.zsh' >> ~/.zshrc
source ~/.zshrc
```

**Fish:**
```fish
socialcli completion fish > ~/.config/fish/completions/socialcli.fish
```

For detailed installation instructions, troubleshooting, and advanced usage, see [docs/COMPLETION.md](docs/COMPLETION.md).

## Claude Code Skill

SocialCLI includes a Claude Code skill that provides an interactive workflow for creating engaging LinkedIn posts with optional comment scheduling. The skill helps with content strategy, writing, formatting, and scheduling - all through a conversational interface.

### Features

- 📝 **Content Creation**: Interactive workflow from ideation to final post
- 💬 **Comment Scheduling**: Schedule one or more comments to boost engagement
- ⏰ **Flexible Timing**: Support for various time formats (5m, 30 minutes, 2h, etc.)
- 🎯 **Best Practices**: Built-in LinkedIn optimization and content guidelines
- 🔄 **Complete Workflow**: From idea to scheduled post and comments

### Installation

The skill is located in `.claude/skills/socialcli-post/`. To use it with Claude Code:

**Option 1: Copy to global skills directory**
```bash
# Copy the skill to your global Claude skills directory
mkdir -p ~/.claude/skills
cp -r .claude/skills/socialcli-post ~/.claude/skills/
```

**Option 2: Use from project directory**

Claude Code will automatically detect skills in the project's `.claude/skills/` directory when working in this repository.

### Usage

When using Claude Code, simply ask to create a LinkedIn post:

```
"I want to create a LinkedIn post"
```

The skill will guide you through:
1. **Content Discovery**: Understanding your goals and audience
2. **Writing**: Crafting engaging content with proper structure
3. **Optimization**: Applying LinkedIn best practices
4. **Scheduling**: Setting publish time and metadata
5. **Comments**: Optional - schedule follow-up comments for engagement

### Comment Scheduling

After creating a post, the skill will ask if you want to schedule comments:

```
User: "I want to add 2 comments"

Skill guides you through:
- Comment 1 text and timing (e.g., "30 minutes after")
- Comment 2 text and timing (e.g., "2 hours after")

Creates:
- Main post file: ~/posts/linkedin-YYYY-MM-DD-title.md
- Comment files: ~/posts/comments/comment-YYYY-MM-DD-HH-MM-title.md
```

**Supported time formats:**
- Minutes: "5m", "30 minutes"
- Hours: "1h", "2 hours"
- Seconds: "300s", "300 seconds"

**Minimum delay:** 5 minutes after the parent post

### Example Workflow

```
You: "Create a post about Python async programming"

Skill: Asks about:
  - Target audience
  - Key points to cover
  - Links to include
  - Tone preference

Skill: Presents draft with optimization suggestions

You: "Perfect! Schedule for tomorrow at 2pm"

Skill: Asks about media, visibility, tags

Skill: Creates post and asks about comments

You: "Add 2 comments - one at 30 minutes and one at 2 hours"

Skill:
  - Creates and schedules main post
  - Creates and schedules both comments
  - Shows summary with all scheduled times
```

### Files Created

**Main posts:** `~/posts/linkedin-YYYY-MM-DD-title.md`
**Comments:** `~/posts/comments/comment-YYYY-MM-DD-HH-MM-title.md`

Make sure the scheduler daemon is running to publish scheduled posts and comments:
```bash
socialcli run-scheduler
```

For more details, see [.claude/skills/socialcli-post/SKILL.md](.claude/skills/socialcli-post/SKILL.md).

## Commands Reference

### `socialcli login`

Authenticate with a social media provider using OAuth 2.0.

```bash
# Login with default provider (LinkedIn)
socialcli login

# Login with specific provider
socialcli login --provider linkedin
```

**Options:**
- `--provider TEXT`: Social provider to authenticate with (default: linkedin)

### `socialcli post`

Create and publish a post or schedule it for later.

```bash
# Post immediately
socialcli post --file my_post.md

# Post with specific provider
socialcli post --file my_post.md --provider linkedin

# Schedule for later (if schedule field in front matter)
socialcli post --file scheduled_post.md
```

**Options:**
- `--file PATH`: Path to markdown file containing the post (required)
- `--provider TEXT`: Provider to use (default: from config or linkedin)

### `socialcli comment`

Add a comment to an existing post.

```bash
# Add a comment
socialcli comment --provider linkedin --target-id POST_ID --text "Great insights!"
```

**Options:**
- `--provider TEXT`: Provider name (required)
- `--target-id TEXT`: ID of the post to comment on (required)
- `--text TEXT`: Comment text (required)

### `socialcli queue`

View and manage scheduled posts.

```bash
# List all scheduled posts
socialcli queue --list

# View queue without options (same as --list)
socialcli queue
```

**Options:**
- `--list`: Display all scheduled posts

### `socialcli prune`

Remove old or completed posts from the queue.

```bash
# Dry run to see what would be deleted
socialcli prune --dry-run

# Delete posts before a specific date
socialcli prune --before 2025-01-01

# Delete posts after a specific date
socialcli prune --after 2024-12-01

# Delete posts within a date range
socialcli prune --after 2024-12-01 --before 2025-01-01

# Delete only completed posts
socialcli prune --status completed --before 2025-01-01

# Delete only failed posts
socialcli prune --status failed
```

**Options:**
- `--before DATE`: Delete posts scheduled before this date (YYYY-MM-DD)
- `--after DATE`: Delete posts scheduled after this date (YYYY-MM-DD)
- `--status TEXT`: Filter by status (pending, completed, failed)
- `--dry-run`: Show what would be deleted without actually deleting

### `socialcli completion`

Generate shell completion scripts for tab completion support.

```bash
# Generate bash completion
socialcli completion bash

# Generate zsh completion
socialcli completion zsh

# Generate fish completion
socialcli completion fish

# Generate PowerShell completion
socialcli completion powershell
```

**Arguments:**
- `SHELL`: Shell type (bash, zsh, fish, or powershell)

See [docs/COMPLETION.md](docs/COMPLETION.md) for installation instructions.

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
