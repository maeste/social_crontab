"""CLI command handlers for SocialCLI.

Provides the main command-line interface using Click framework.
Commands:
- login: Authenticate with a social provider
- post: Create and publish posts
- comment: Add comments to posts
- queue: Manage scheduled posts
- prune: Remove published posts from storage
"""

import click
from socialcli.core.storage import Storage


@click.group()
@click.version_option()
def cli():
    """SocialCLI - Manage social media posts from the command line."""
    pass


@cli.command()
@click.option('--provider', default='linkedin', help='Social provider to authenticate with')
def login(provider):
    """Authenticate with a social provider."""
    click.echo(f"Login command for provider: {provider}")


@cli.command()
@click.option('--file', required=True, help='Path to post file (markdown or text)')
@click.option('--provider', default='linkedin', help='Social provider to post to')
def post(file, provider):
    """Create and publish a post."""
    click.echo(f"Post command - file: {file}, provider: {provider}")


@cli.command()
@click.option('--provider', required=True, help='Social provider')
@click.option('--target-id', required=True, help='Target post ID')
@click.option('--text', required=True, help='Comment text')
def comment(provider, target_id, text):
    """Add a comment to a post."""
    click.echo(f"Comment command - provider: {provider}, target: {target_id}")


@cli.command()
@click.option('--list', 'list_queue', is_flag=True, help='List scheduled posts')
def queue(list_queue):
    """Manage scheduled posts."""
    if list_queue:
        click.echo("Listing scheduled posts...")


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


if __name__ == '__main__':
    cli()
