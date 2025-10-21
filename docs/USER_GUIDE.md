# SocialCLI User Guide

Complete guide to using SocialCLI for managing your social media posts from the command line.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [Creating Posts](#creating-posts)
- [Scheduling Posts](#scheduling-posts)
- [Managing Comments](#managing-comments)
- [Queue Management](#queue-management)
- [Workflows and Examples](#workflows-and-examples)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/socialcli.git
   cd socialcli
   ```

2. **Install the package:**
   ```bash
   # Using pip (recommended for users)
   pip install -e .

   # Using uv (for development)
   uv venv
   source .venv/bin/activate  # On Linux/Mac
   uv pip install -e ".[dev]"
   ```

3. **Verify installation:**
   ```bash
   socialcli --version
   # Should output: socialcli, version 0.1.0
   ```

### First Steps

1. Create configuration directory:
   ```bash
   mkdir -p ~/.socialcli
   ```

2. Set up your configuration (see [Configuration](#configuration) section)

3. Authenticate with LinkedIn (see [Authentication](#authentication) section)

4. Create your first post!

## Configuration

### Configuration File

SocialCLI uses a YAML configuration file located at `~/.socialcli/config.yaml`.

### Basic Configuration

Create `~/.socialcli/config.yaml` with the following content:

```yaml
providers:
  linkedin:
    # OAuth 2.0 credentials from LinkedIn Developer Portal
    # Get yours at: https://www.linkedin.com/developers/apps
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET

    # OAuth redirect URI (must match what's registered in LinkedIn app)
    redirect_uri: http://localhost:8080/callback

    # Optional: Custom scopes (defaults shown below)
    scopes:
      - openid
      - profile
      - email
      - w_member_social

# Storage settings (optional)
storage:
  base_path: ~/.socialcli
  db_file: posts.db

# Scheduler settings (optional)
scheduler:
  check_interval: 60  # seconds
  enabled: true

# Logging settings (optional)
logging:
  level: INFO
  file: ~/.socialcli/socialcli.log
```

### Getting LinkedIn Credentials

1. **Create a LinkedIn App:**
   - Go to https://www.linkedin.com/developers/apps
   - Click "Create app"
   - Fill in app details

2. **Configure OAuth 2.0:**
   - Go to the "Auth" tab in your app
   - Add redirect URL: `http://localhost:8080/callback`
   - Request the following scopes:
     - `openid`
     - `profile`
     - `email`
     - `w_member_social`

3. **Copy Credentials:**
   - Copy your Client ID and Client Secret
   - Add them to `~/.socialcli/config.yaml`

### Configuration Schema

```yaml
providers:
  <provider_name>:
    client_id: string       # Required: OAuth client ID
    client_secret: string   # Required: OAuth client secret
    access_token: string    # Auto-filled after login
    refresh_token: string   # Auto-filled after login
    token_expiry: string    # Auto-filled after login
    redirect_uri: string    # Optional: Custom redirect URI
    scopes: list            # Optional: Custom OAuth scopes

storage:
  base_path: string         # Default: ~/.socialcli
  db_file: string           # Default: posts.db

scheduler:
  check_interval: int       # Default: 60 (seconds)
  enabled: bool             # Default: true

logging:
  level: string             # Default: INFO
  file: string              # Default: ~/.socialcli/socialcli.log
  format: string            # Default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Authentication

### Login Command

Authenticate with a social media provider using OAuth 2.0:

```bash
# Login with default provider (LinkedIn)
socialcli login

# Login with specific provider
socialcli login --provider linkedin
```

### What Happens During Login

1. SocialCLI starts a local web server on port 8080
2. Opens your browser to LinkedIn's authorization page
3. You grant permissions to the app
4. LinkedIn redirects back to localhost with an authorization code
5. SocialCLI exchanges the code for an access token
6. Token is saved to your config file automatically

### Verifying Authentication

After successful login, your config file will be updated with:
- `access_token`: Used for API calls
- `refresh_token`: Used to renew expired tokens
- `token_expiry`: When the current token expires

You can verify by checking `~/.socialcli/config.yaml`.

### Token Refresh

SocialCLI automatically refreshes expired tokens when needed. You don't need to manually manage token expiration.

## Creating Posts

### Post File Format

Posts are written in Markdown with optional YAML front matter.

#### Simple Text Post

```markdown
💬 Agents, AI, and Humility

Karpathy's latest interview sparks an important point: tools evolve, but humility must remain.

As AI capabilities expand, developers must balance confidence with curiosity.

#AI #AgenticAI #Development
```

#### Post with Front Matter

```markdown
---
platform: linkedin
visibility: public
tags: [AI, Agents, Development]
---

💬 Agents, AI, and Humility

Karpathy's latest interview sparks an important point: tools evolve, but humility must remain.

As AI capabilities expand, developers must balance confidence with curiosity.

#AI #AgenticAI #Development
```

### Front Matter Fields

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `platform` | string | Target platform (linkedin, x, etc.) | linkedin |
| `visibility` | string | Post visibility (public, connections) | public |
| `tags` | list | Tags/categories for organization | [] |
| `schedule` | datetime | When to publish (ISO 8601 format) | now |
| `media` | list | Paths to images/media files | [] |

### Publishing a Post

```bash
# Post immediately with default provider
socialcli post --file my_post.md

# Post with specific provider
socialcli post --file my_post.md --provider linkedin
```

### Post with Images

Create a post file with media in front matter:

```markdown
---
platform: linkedin
visibility: public
media:
  - /path/to/image1.jpg
  - /path/to/image2.png
---

Check out these amazing visualizations! 📊

#DataViz #Analytics
```

Then post it:

```bash
socialcli post --file post_with_images.md
```

## Scheduling Posts

### Creating Scheduled Posts

Add a `schedule` field to your post's front matter:

```markdown
---
platform: linkedin
visibility: public
schedule: 2025-12-25T09:00:00
---

🎄 Merry Christmas from the team!

Wishing everyone a wonderful holiday season.

#HappyHolidays
```

### Scheduling Format

Use ISO 8601 format for schedules:
- `2025-12-25T09:00:00` - Local time
- `2025-12-25T09:00:00Z` - UTC time
- `2025-12-25T09:00:00-05:00` - With timezone offset

### Posting Scheduled Content

```bash
# This will queue the post for scheduled publication
socialcli post --file scheduled_post.md
```

The post will be added to the queue and published automatically when the scheduled time arrives.

### Scheduler Daemon

The scheduler runs automatically and checks for due posts every 60 seconds (configurable).

To modify the check interval, update your config:

```yaml
scheduler:
  check_interval: 30  # Check every 30 seconds
  enabled: true
```

## Managing Comments

### Adding Comments

```bash
# Add a comment to a post
socialcli comment \
  --provider linkedin \
  --target-id POST_URN \
  --text "Great insights! Thanks for sharing."
```

### Finding Post IDs

LinkedIn post IDs (URNs) look like:
- `urn:li:share:1234567890`
- `urn:li:ugcPost:1234567890`

You can find them in the LinkedIn API response after posting.

### Comment Best Practices

- Keep comments concise and relevant
- Use proper formatting
- Avoid spam or repetitive comments
- Respect community guidelines

## Queue Management

### Viewing Scheduled Posts

```bash
# List all scheduled posts
socialcli queue --list

# Or simply:
socialcli queue
```

### Queue Output

```
ID  Provider  Author      File                    Scheduled At          Status
==  ========  ==========  ======================  ====================  =========
1   linkedin  @username   posts/morning.md        2025-12-25 09:00:00   pending
2   linkedin  @username   posts/afternoon.md      2025-12-25 14:00:00   pending
3   linkedin  @username   posts/evening.md        2025-12-25 18:00:00   completed
```

### Post Statuses

- `pending`: Waiting to be published
- `completed`: Successfully published
- `failed`: Publication failed (check logs)

### Pruning Old Posts

Remove completed or old posts from the queue:

```bash
# Dry run to see what would be deleted
socialcli prune --dry-run

# Delete completed posts before a date
socialcli prune --status completed --before 2025-01-01

# Delete failed posts
socialcli prune --status failed

# Delete all posts in a date range
socialcli prune --after 2024-12-01 --before 2025-01-01
```

### Prune Options

- `--before DATE`: Delete posts scheduled before this date (YYYY-MM-DD)
- `--after DATE`: Delete posts scheduled after this date (YYYY-MM-DD)
- `--status TEXT`: Filter by status (pending, completed, failed)
- `--dry-run`: Preview deletions without actually deleting

## Workflows and Examples

### Daily Posting Workflow

1. **Morning: Create post**
   ```bash
   # Create posts/morning.md
   cat > posts/morning.md << 'EOF'
   ---
   platform: linkedin
   visibility: public
   ---

   Good morning! Here's today's thought...
   EOF
   ```

2. **Post immediately**
   ```bash
   socialcli post --file posts/morning.md
   ```

### Weekly Content Schedule

1. **Sunday: Plan the week**
   ```bash
   # Create posts for the entire week
   for day in monday tuesday wednesday thursday friday; do
     cat > posts/${day}.md << 'EOF'
   ---
   schedule: 2025-10-$(date for $day)T09:00:00
   ---

   ${day} motivation post...
   EOF
   done
   ```

2. **Queue all posts**
   ```bash
   for day in monday tuesday wednesday thursday friday; do
     socialcli post --file posts/${day}.md
   done
   ```

3. **Verify queue**
   ```bash
   socialcli queue --list
   ```

4. **Friday: Clean up completed posts**
   ```bash
   socialcli prune --status completed --before $(date +%Y-%m-%d)
   ```

### Batch Commenting

```bash
# Comment on multiple posts
for post_id in URN1 URN2 URN3; do
  socialcli comment \
    --provider linkedin \
    --target-id $post_id \
    --text "Thanks for sharing!"
done
```

### Content Calendar Integration

```bash
# Export queue to CSV for calendar apps
socialcli queue --list > schedule.txt
```

## Troubleshooting

### Authentication Issues

**Problem:** Login fails or returns error

**Solutions:**
1. Verify client ID and secret in config
2. Check redirect URI matches LinkedIn app settings
3. Ensure required scopes are requested
4. Clear browser cache and try again

**Problem:** Token expired errors

**Solutions:**
1. Run `socialcli login` again to refresh
2. Check if refresh token is present in config
3. Verify token expiry date

### Posting Issues

**Problem:** Post fails to publish

**Solutions:**
1. Check authentication: `socialcli login`
2. Verify post file format (valid YAML, Markdown)
3. Check file path is correct
4. Review logs: `~/.socialcli/socialcli.log`

**Problem:** Media upload fails

**Solutions:**
1. Verify image file exists and is readable
2. Check file format (JPG, PNG supported)
3. Ensure file size is within LinkedIn limits
4. Use absolute paths for media files

### Scheduler Issues

**Problem:** Scheduled posts not publishing

**Solutions:**
1. Verify scheduler is enabled in config
2. Check system time is correct
3. Review scheduler logs
4. Ensure scheduled time is in the future

**Problem:** Queue shows wrong times

**Solutions:**
1. Use correct ISO 8601 format
2. Specify timezone if needed
3. Verify system timezone settings

### Configuration Issues

**Problem:** Config file not found

**Solutions:**
1. Create directory: `mkdir -p ~/.socialcli`
2. Create config file: `touch ~/.socialcli/config.yaml`
3. Add provider configuration

**Problem:** Invalid YAML syntax

**Solutions:**
1. Use YAML validator online
2. Check indentation (use spaces, not tabs)
3. Ensure colons have spaces after them
4. Quote strings with special characters

### Getting Help

1. **Check logs:**
   ```bash
   tail -f ~/.socialcli/socialcli.log
   ```

2. **Enable debug logging:**
   ```yaml
   # In config.yaml
   logging:
     level: DEBUG
   ```

3. **Test configuration:**
   ```bash
   socialcli --help
   socialcli login --help
   ```

4. **Report issues:**
   - GitHub Issues: https://github.com/yourusername/socialcli/issues
   - Include log files and error messages
   - Describe steps to reproduce

## Advanced Usage

### Custom Configuration Location

```bash
# Use custom config file
export SOCIALCLI_CONFIG=~/my-custom-config.yaml
socialcli post --file post.md
```

### Multiple Accounts

Create separate config files for each account:

```bash
# Account 1 (personal)
socialcli --config ~/.socialcli/personal.yaml login
socialcli --config ~/.socialcli/personal.yaml post --file post.md

# Account 2 (work)
socialcli --config ~/.socialcli/work.yaml login
socialcli --config ~/.socialcli/work.yaml post --file post.md
```

### Automation with Cron

Add to your crontab:

```cron
# Post every weekday at 9 AM
0 9 * * 1-5 cd ~/posts && socialcli post --file daily.md

# Clean up queue every Sunday at midnight
0 0 * * 0 socialcli prune --status completed --before $(date +%Y-%m-%d)
```

### Scripting Examples

```bash
#!/bin/bash
# post_batch.sh - Post multiple files

for file in posts/*.md; do
  echo "Posting $file..."
  socialcli post --file "$file"
  sleep 5  # Rate limiting
done
```

## Best Practices

### Post Content

- ✅ Keep posts concise and engaging
- ✅ Use relevant hashtags (3-5 recommended)
- ✅ Include emojis for visual appeal
- ✅ Proofread before posting
- ❌ Avoid excessive hashtags
- ❌ Don't post duplicate content

### Scheduling

- ✅ Schedule during peak engagement times
- ✅ Maintain consistent posting schedule
- ✅ Use queue to plan content ahead
- ✅ Review scheduled posts before they go live
- ❌ Don't over-schedule (quality > quantity)
- ❌ Avoid scheduling too far in advance

### Security

- ✅ Keep config files private (chmod 600)
- ✅ Never commit tokens to version control
- ✅ Use environment variables for CI/CD
- ✅ Rotate credentials periodically
- ❌ Don't share client secrets
- ❌ Avoid storing credentials in scripts

### Organization

- ✅ Use descriptive file names
- ✅ Organize posts by topic/date
- ✅ Keep a content calendar
- ✅ Tag posts for easy searching
- ❌ Don't let queue become cluttered
- ❌ Avoid disorganized post files

## Appendix

### Supported Platforms

| Platform | Status | Post | Comment | Media | Schedule |
|----------|--------|------|---------|-------|----------|
| LinkedIn | ✅ MVP | ✅ | ✅ | ✅ | ✅ |
| X (Twitter) | 📋 Planned | - | - | - | - |
| Threads | 📋 Planned | - | - | - | - |
| Bluesky | 📋 Planned | - | - | - | - |
| Mastodon | 📋 Planned | - | - | - | - |

### CLI Command Quick Reference

```bash
# Authentication
socialcli login [--provider TEXT]

# Posting
socialcli post --file PATH [--provider TEXT]

# Comments
socialcli comment --provider TEXT --target-id TEXT --text TEXT

# Queue Management
socialcli queue [--list]
socialcli prune [--before DATE] [--after DATE] [--status TEXT] [--dry-run]

# Help
socialcli --help
socialcli <command> --help
```

### File Locations

- Config: `~/.socialcli/config.yaml`
- Database: `~/.socialcli/posts.db`
- Logs: `~/.socialcli/socialcli.log`
- Posts: User-defined (recommended: `~/posts/`)

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Authentication error
- `4`: API error

---

**Questions or feedback?** Open an issue on GitHub or check the main README for more information.
