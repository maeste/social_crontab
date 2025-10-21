"""Tests for CLI framework and commands."""

import pytest
from click.testing import CliRunner
from socialcli.core.cli import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


class TestCLIFramework:
    """Test CLI framework structure and main command group."""

    def test_cli_main_command_exists(self, runner):
        """Test that main CLI command group exists."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'SocialCLI' in result.output
        assert 'Manage social media posts from the command line' in result.output

    def test_cli_shows_version(self, runner):
        """Test that --version flag displays version info."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
        assert '0.1.0' in result.output

    def test_cli_shows_available_commands(self, runner):
        """Test that help text shows all available subcommands."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Check all expected commands are listed
        assert 'login' in result.output
        assert 'post' in result.output
        assert 'comment' in result.output
        assert 'queue' in result.output
        assert 'prune' in result.output

    def test_cli_invalid_command_fails(self, runner):
        """Test that invalid command shows error."""
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'No such command' in result.output


class TestLoginCommand:
    """Test login command."""

    def test_login_command_exists(self, runner):
        """Test that login command is registered."""
        result = runner.invoke(cli, ['login', '--help'])
        assert result.exit_code == 0
        assert 'Authenticate with a social provider' in result.output

    def test_login_default_provider(self, runner):
        """Test login with default provider (linkedin)."""
        result = runner.invoke(cli, ['login'])
        assert result.exit_code == 0
        assert 'linkedin' in result.output.lower()

    def test_login_custom_provider(self, runner):
        """Test login with custom provider."""
        result = runner.invoke(cli, ['login', '--provider', 'twitter'])
        assert result.exit_code == 0
        assert 'twitter' in result.output.lower()

    def test_login_help_shows_provider_option(self, runner):
        """Test that login help shows provider option."""
        result = runner.invoke(cli, ['login', '--help'])
        assert result.exit_code == 0
        assert '--provider' in result.output


class TestPostCommand:
    """Test post command."""

    def test_post_command_exists(self, runner):
        """Test that post command is registered."""
        result = runner.invoke(cli, ['post', '--help'])
        assert result.exit_code == 0
        assert 'Create and publish a post' in result.output

    def test_post_requires_file(self, runner):
        """Test that post command requires --file option."""
        result = runner.invoke(cli, ['post'])
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()

    def test_post_with_file(self, runner):
        """Test post command with file option."""
        result = runner.invoke(cli, ['post', '--file', 'test.md'])
        assert result.exit_code == 0
        assert 'test.md' in result.output

    def test_post_with_provider(self, runner):
        """Test post command with custom provider."""
        result = runner.invoke(cli, ['post', '--file', 'test.md', '--provider', 'twitter'])
        assert result.exit_code == 0
        assert 'twitter' in result.output.lower()

    def test_post_help_shows_options(self, runner):
        """Test that post help shows file and provider options."""
        result = runner.invoke(cli, ['post', '--help'])
        assert result.exit_code == 0
        assert '--file' in result.output
        assert '--provider' in result.output


class TestCommentCommand:
    """Test comment command."""

    def test_comment_command_exists(self, runner):
        """Test that comment command is registered."""
        result = runner.invoke(cli, ['comment', '--help'])
        assert result.exit_code == 0
        assert 'Add a comment to a post' in result.output

    def test_comment_requires_provider(self, runner):
        """Test that comment command requires provider."""
        result = runner.invoke(cli, ['comment'])
        assert result.exit_code != 0

    def test_comment_requires_target_id(self, runner):
        """Test that comment command requires target-id."""
        result = runner.invoke(cli, ['comment', '--provider', 'linkedin'])
        assert result.exit_code != 0

    def test_comment_requires_text(self, runner):
        """Test that comment command requires text."""
        result = runner.invoke(cli, ['comment', '--provider', 'linkedin', '--target-id', '123'])
        assert result.exit_code != 0

    def test_comment_with_all_options(self, runner):
        """Test comment command with all required options."""
        result = runner.invoke(cli, [
            'comment',
            '--provider', 'linkedin',
            '--target-id', '12345',
            '--text', 'Great post!'
        ])
        assert result.exit_code == 0
        assert 'linkedin' in result.output.lower()
        assert '12345' in result.output


class TestQueueCommand:
    """Test queue command."""

    def test_queue_command_exists(self, runner):
        """Test that queue command is registered."""
        result = runner.invoke(cli, ['queue', '--help'])
        assert result.exit_code == 0
        assert 'Manage scheduled posts' in result.output

    def test_queue_without_options(self, runner):
        """Test queue command without options."""
        result = runner.invoke(cli, ['queue'])
        assert result.exit_code == 0

    def test_queue_list_flag(self, runner):
        """Test queue command with --list flag."""
        result = runner.invoke(cli, ['queue', '--list'])
        assert result.exit_code == 0
        assert 'Listing' in result.output or 'scheduled' in result.output.lower()


class TestPruneCommand:
    """Test prune command."""

    def test_prune_command_exists(self, runner):
        """Test that prune command is registered."""
        result = runner.invoke(cli, ['prune', '--help'])
        assert result.exit_code == 0
        assert 'Remove published posts' in result.output

    def test_prune_help_shows_examples(self, runner):
        """Test that prune help shows usage examples."""
        result = runner.invoke(cli, ['prune', '--help'])
        assert result.exit_code == 0
        assert 'Examples:' in result.output
        assert '--before' in result.output
        assert '--after' in result.output

    def test_prune_help_shows_all_options(self, runner):
        """Test that prune help shows all available options."""
        result = runner.invoke(cli, ['prune', '--help'])
        assert result.exit_code == 0
        assert '--before' in result.output
        assert '--after' in result.output
        assert '--status' in result.output
        assert '--dry-run' in result.output

    def test_prune_dry_run_flag(self, runner):
        """Test prune command with --dry-run flag."""
        result = runner.invoke(cli, ['prune', '--dry-run'])
        assert result.exit_code == 0
        # Should show preview message
        assert 'Would prune' in result.output or 'No posts' in result.output

    def test_prune_with_before_date(self, runner):
        """Test prune command with --before option."""
        result = runner.invoke(cli, ['prune', '--before', '2025-10-01', '--dry-run'])
        assert result.exit_code == 0

    def test_prune_with_after_date(self, runner):
        """Test prune command with --after option."""
        result = runner.invoke(cli, ['prune', '--after', '2025-09-01', '--dry-run'])
        assert result.exit_code == 0

    def test_prune_with_date_range(self, runner):
        """Test prune command with both before and after dates."""
        result = runner.invoke(cli, [
            'prune',
            '--after', '2025-09-01',
            '--before', '2025-10-01',
            '--dry-run'
        ])
        assert result.exit_code == 0

    def test_prune_invalid_date_format_before(self, runner):
        """Test prune rejects invalid date format for --before."""
        result = runner.invoke(cli, ['prune', '--before', 'invalid-date'])
        assert result.exit_code == 0  # Command runs but shows error
        assert 'Error' in result.output or 'Invalid' in result.output

    def test_prune_invalid_date_format_after(self, runner):
        """Test prune rejects invalid date format for --after."""
        result = runner.invoke(cli, ['prune', '--after', '10/01/2025'])
        assert result.exit_code == 0  # Command runs but shows error
        assert 'Error' in result.output or 'Invalid' in result.output

    def test_prune_custom_status(self, runner):
        """Test prune command with custom status."""
        result = runner.invoke(cli, ['prune', '--status', 'failed', '--dry-run'])
        assert result.exit_code == 0


class TestCLIIntegration:
    """Test CLI integration and overall functionality."""

    def test_all_commands_accessible(self, runner):
        """Test that all commands can be invoked without errors."""
        commands = ['login', 'post', 'comment', 'queue', 'prune']

        for command in commands:
            result = runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0, f"Command {command} failed"

    def test_main_group_help_formatting(self, runner):
        """Test that main help text is properly formatted."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0

        # Check for proper sections
        assert 'Usage:' in result.output
        assert 'Options:' in result.output
        assert 'Commands:' in result.output

    def test_command_help_formatting(self, runner):
        """Test that individual command help is properly formatted."""
        result = runner.invoke(cli, ['post', '--help'])
        assert result.exit_code == 0

        # Check for proper sections
        assert 'Usage:' in result.output
        assert 'Options:' in result.output
