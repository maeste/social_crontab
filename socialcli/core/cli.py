"""CLI command handlers for SocialCLI.

Provides the main command-line interface using Click framework.
Commands:
- login: Authenticate with a social provider
- post: Create and publish posts
- comment: Add comments to posts
- queue: Manage scheduled posts
- run-scheduler: Execute scheduled posts at the correct times
- prune: Remove published posts from storage
"""

import click
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path

from socialcli.core.storage import Storage
from socialcli.core.config import Config, ProviderConfig
from socialcli.core.scheduler_daemon import SchedulerDaemon
from socialcli.utils.parser import PostParser
from socialcli.providers.linkedin.auth import LinkedInAuth
from socialcli.providers.linkedin.provider import LinkedInProvider
from socialcli.providers.base import AuthenticationError, PostError, CommentError


# OAuth callback handler
class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    auth_code = None

    def do_GET(self):
        """Handle OAuth callback GET request."""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            CallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params.get('error', ['Unknown error'])[0]
            self.wfile.write(f"<h1>Authentication Failed</h1><p>Error: {error}</p>".encode())

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


@click.group()
@click.version_option()
def cli():
    """SocialCLI - Manage social media posts from the command line."""
    pass


@cli.command()
@click.option('--provider', default='linkedin', help='Social provider to authenticate with')
def login(provider):
    """Authenticate with a social provider.

    Opens a browser for OAuth authentication and stores the access token.

    Example:
        socialcli login --provider linkedin
    """
    try:
        # Load config
        config = Config.load(validate=False)
        provider_config = config.get_provider_config(provider)

        if not provider_config:
            click.echo(f"Error: Provider '{provider}' not configured.", err=True)
            click.echo(f"Please add {provider} configuration to ~/.socialcli/config.yaml", err=True)
            click.echo("\nExample config:")
            click.echo("providers:")
            click.echo(f"  {provider}:")
            click.echo("    client_id: your_client_id")
            click.echo("    client_secret: your_client_secret")
            sys.exit(1)

        if not provider_config.client_id or not provider_config.client_secret:
            click.echo(f"Error: Missing credentials for {provider}", err=True)
            click.echo(f"Please update ~/.socialcli/config.yaml with client_id and client_secret", err=True)
            sys.exit(1)

        # Currently only LinkedIn is supported
        if provider != 'linkedin':
            click.echo(f"Error: Provider '{provider}' not yet implemented.", err=True)
            click.echo("Currently supported: linkedin")
            sys.exit(1)

        # Initialize LinkedIn auth
        auth = LinkedInAuth(
            client_id=provider_config.client_id,
            client_secret=provider_config.client_secret,
            redirect_uri="http://localhost:8080/callback",
            config=config
        )

        # Check if already authenticated
        if auth.is_authenticated():
            click.echo(f"✓ Already authenticated with {provider}")

            # Verify authentication by getting profile
            linkedin = LinkedInProvider(
                client_id=provider_config.client_id,
                client_secret=provider_config.client_secret,
                config=config
            )

            try:
                profile = linkedin.get_profile()
                click.echo(f"✓ Logged in as: {profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}")
                return
            except Exception as e:
                click.echo(f"⚠ Token may be invalid: {e}", err=True)
                click.echo("Requesting new authentication...")

        # Get authorization URL
        auth_url = auth.get_authorization_url()

        click.echo(f"Opening browser for {provider} authentication...")
        click.echo(f"If browser doesn't open, visit: {auth_url}")

        # Open browser
        webbrowser.open(auth_url)

        # Start local server for callback
        click.echo("Waiting for authorization...")
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        server.handle_request()

        if not CallbackHandler.auth_code:
            click.echo("Error: No authorization code received", err=True)
            sys.exit(1)

        # Exchange code for token
        click.echo("Exchanging authorization code for access token...")
        token_data = auth.exchange_code_for_token(CallbackHandler.auth_code)

        # Save tokens
        auth.save_tokens(token_data)

        # Verify authentication
        linkedin = LinkedInProvider(
            client_id=provider_config.client_id,
            client_secret=provider_config.client_secret,
            config=config
        )

        profile = linkedin.get_profile()

        click.echo(f"✓ Successfully authenticated with {provider}")
        click.echo(f"✓ Logged in as: {profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}")

    except Exception as e:
        click.echo(f"Error during login: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', required=True, help='Path to post file (markdown or text)')
@click.option('--provider', default='linkedin', help='Social provider to post to')
def post(file, provider):
    """Create and publish a post from a file.

    The post file can be plain text or markdown with optional YAML front matter
    for metadata like schedule time, tags, etc.

    Examples:
        socialcli post --file mypost.md --provider linkedin
        socialcli post --file mypost.txt

    Front matter example:
        ---
        schedule: 2025-10-22T10:00:00
        tags: [tech, ai]
        ---
        Post content here...
    """
    try:
        # Parse post file
        try:
            parser = PostParser(file)
            parser.validate()
        except FileNotFoundError:
            click.echo(f"Error: Post file not found: {file}", err=True)
            sys.exit(1)
        except ValueError as e:
            click.echo(f"Error: Invalid post file: {e}", err=True)
            sys.exit(1)

        content = parser.get_content()
        schedule = parser.get_schedule()
        file_provider = parser.get_provider() or provider

        # Load config
        config = Config.load(validate=False)
        provider_config = config.get_provider_config(file_provider)

        if not provider_config or not provider_config.is_authenticated():
            click.echo(f"Error: Not authenticated with {file_provider}", err=True)
            click.echo(f"Run: socialcli login --provider {file_provider}")
            sys.exit(1)

        # Initialize storage
        storage = Storage()

        # If scheduled, save to database
        if schedule:
            schedule_dt = datetime.fromisoformat(schedule)
            now = datetime.now()

            if schedule_dt <= now:
                click.echo(f"Error: Schedule time must be in the future", err=True)
                sys.exit(1)

            # Create scheduled post
            post_id = storage.create_scheduled_post(
                provider=file_provider,
                author="user",  # Will be enhanced in scheduler
                file_path=str(Path(file).resolve()),
                publish_at=schedule,
                status="pending"
            )

            click.echo(f"✓ Post scheduled for {schedule}")
            click.echo(f"✓ Post ID: {post_id}")
            click.echo(f"✓ Run 'socialcli queue --list' to see all scheduled posts")
            return

        # Post immediately
        if file_provider != 'linkedin':
            click.echo(f"Error: Provider '{file_provider}' not yet implemented.", err=True)
            sys.exit(1)

        linkedin = LinkedInProvider(
            client_id=provider_config.client_id,
            client_secret=provider_config.client_secret,
            config=config
        )

        click.echo(f"Publishing to {file_provider}...")

        result = linkedin.post(content)

        click.echo(f"✓ Post published successfully!")
        if 'id' in result:
            click.echo(f"✓ Post ID: {result['id']}")

    except PostError as e:
        click.echo(f"Error posting: {e}", err=True)
        sys.exit(1)
    except AuthenticationError as e:
        click.echo(f"Authentication error: {e}", err=True)
        click.echo(f"Run: socialcli login --provider {provider}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--provider', required=True, help='Social provider')
@click.option('--target-id', required=True, help='Target post ID/URN')
@click.option('--text', required=True, help='Comment text')
def comment(provider, target_id, text):
    """Add a comment to a post.

    Examples:
        socialcli comment --provider linkedin --target-id "urn:li:share:123456" --text "Great post!"
    """
    try:
        # Load config
        config = Config.load(validate=False)
        provider_config = config.get_provider_config(provider)

        if not provider_config or not provider_config.is_authenticated():
            click.echo(f"Error: Not authenticated with {provider}", err=True)
            click.echo(f"Run: socialcli login --provider {provider}")
            sys.exit(1)

        # Currently only LinkedIn is supported
        if provider != 'linkedin':
            click.echo(f"Error: Provider '{provider}' not yet implemented.", err=True)
            sys.exit(1)

        linkedin = LinkedInProvider(
            client_id=provider_config.client_id,
            client_secret=provider_config.client_secret,
            config=config
        )

        click.echo(f"Adding comment to {target_id}...")

        result = linkedin.comment(target_id, text)

        click.echo(f"✓ Comment posted successfully!")
        if 'id' in result:
            click.echo(f"✓ Comment ID: {result['id']}")

    except CommentError as e:
        click.echo(f"Error commenting: {e}", err=True)
        sys.exit(1)
    except AuthenticationError as e:
        click.echo(f"Authentication error: {e}", err=True)
        click.echo(f"Run: socialcli login --provider {provider}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--list', 'list_queue', is_flag=True, help='List scheduled posts')
@click.option('--provider', help='Filter by provider')
@click.option('--status', help='Filter by status (pending, published, failed)')
def queue(list_queue, provider, status):
    """Manage scheduled posts.

    Examples:
        socialcli queue --list
        socialcli queue --list --provider linkedin
        socialcli queue --list --status pending
    """
    if list_queue:
        storage = Storage()

        # Get scheduled posts with optional filters
        posts = storage.get_all_scheduled_posts(status=status, provider=provider)

        if not posts:
            click.echo("No scheduled posts found.")
            return

        click.echo(f"\nScheduled Posts ({len(posts)}):")
        click.echo("=" * 80)

        for p in posts:
            click.echo(f"\nID: {p['id']}")
            click.echo(f"Provider: {p['provider']}")
            click.echo(f"Status: {p['status']}")
            click.echo(f"Publish at: {p['publish_at']}")
            click.echo(f"File: {p['file_path']}")
            click.echo(f"Created: {p['created_at']}")
            if 'updated_at' in p:
                click.echo(f"Updated: {p['updated_at']}")
            click.echo("-" * 80)
    else:
        click.echo("Use --list to see scheduled posts")
        click.echo("Example: socialcli queue --list")


@cli.command()
@click.option('--before', help='Prune posts published before this date (ISO format: YYYY-MM-DD)')
@click.option('--after', help='Prune posts published after this date (ISO format: YYYY-MM-DD)')
@click.option('--status', default='published', help='Only prune posts with this status (default: published)')
@click.option('--dry-run', is_flag=True, help='Show what would be pruned without actually deleting')
def prune(before, after, status, dry_run):
    """Remove published posts from storage to keep the database clean.

    Examples:
        socialcli prune                              # Prune all published posts
        socialcli prune --before 2025-10-01          # Prune posts before Oct 1, 2025
        socialcli prune --after 2025-09-01           # Prune posts after Sep 1, 2025
        socialcli prune --after 2025-09-01 --before 2025-10-01  # Prune date range
        socialcli prune --dry-run                    # Preview what would be pruned
    """
    storage = Storage()

    # Validate date formats if provided
    if before or after:
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}'
        if before and not re.match(date_pattern, before):
            click.echo(f"Error: Invalid date format for --before. Use YYYY-MM-DD", err=True)
            return
        if after and not re.match(date_pattern, after):
            click.echo(f"Error: Invalid date format for --after. Use YYYY-MM-DD", err=True)
            return

    # Show what will be pruned if dry-run
    if dry_run:
        posts = storage.get_all_scheduled_posts(status=status)

        def matches_criteria(post):
            publish_at = post.get('publish_at', '')
            if before and publish_at >= before:
                return False
            if after and publish_at <= after:
                return False
            return True

        to_prune = [p for p in posts if matches_criteria(p)]

        if to_prune:
            click.echo(f"Would prune {len(to_prune)} post(s):")
            for post in to_prune:
                click.echo(f"  - ID {post['id']}: {post['provider']} post at {post['publish_at']}")
        else:
            click.echo("No posts match the pruning criteria.")
        return

    # Actually prune
    pruned_count = storage.prune_scheduled_posts(
        before=before,
        after=after,
        status=status
    )

    if pruned_count > 0:
        click.echo(f"Successfully pruned {pruned_count} post(s).")
    else:
        click.echo("No posts were pruned.")


@cli.command()
@click.option('--interval', default=60, help='Check interval in seconds (default: 60)')
@click.option('--once', is_flag=True, help='Run once and exit (for testing)')
def run_scheduler(interval, once):
    """Run the scheduler daemon to execute scheduled posts.

    The scheduler continuously monitors scheduled posts and publishes them
    at the appropriate times. It runs in the foreground and can be stopped
    with Ctrl+C.

    Examples:
        socialcli run-scheduler                    # Run with default 60s interval
        socialcli run-scheduler --interval 30      # Check every 30 seconds
        socialcli run-scheduler --once             # Process pending posts once and exit
    """
    try:
        daemon = SchedulerDaemon(check_interval=interval)

        if once:
            daemon.run_once()
        else:
            click.echo(f"Starting scheduler daemon (check interval: {interval}s)")
            click.echo("Press Ctrl+C to stop")
            daemon.run()
    except KeyboardInterrupt:
        click.echo("\nScheduler stopped by user")
    except Exception as e:
        click.echo(f"Error running scheduler: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
