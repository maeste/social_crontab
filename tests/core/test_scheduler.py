"""Tests for scheduler daemon functionality."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from socialcli.core.scheduler_daemon import SchedulerDaemon
from socialcli.core.storage import Storage


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage instance for testing."""
    return Storage(base_path=tmp_path)


@pytest.fixture
def scheduler(temp_storage):
    """Create a scheduler daemon instance for testing."""
    return SchedulerDaemon(storage=temp_storage, check_interval=1)


@pytest.fixture
def sample_post_file(tmp_path):
    """Create a sample post file for testing."""
    post_dir = tmp_path / 'posts'
    post_dir.mkdir(parents=True, exist_ok=True)
    post_file = post_dir / 'test_post.md'
    post_file.write_text("""---
platform: linkedin
visibility: public
---

This is a test post for scheduler.""", encoding='utf-8')
    return post_file


class TestSchedulerInitialization:
    """Test scheduler daemon initialization."""

    def test_init_with_storage(self, temp_storage):
        """Test scheduler initialization with provided storage."""
        scheduler = SchedulerDaemon(storage=temp_storage, check_interval=30)
        assert scheduler.storage == temp_storage
        assert scheduler.check_interval == 30
        assert scheduler.running is False

    def test_init_without_storage(self):
        """Test scheduler initialization creates default storage."""
        scheduler = SchedulerDaemon()
        assert scheduler.storage is not None
        assert scheduler.check_interval == 60


class TestProviderInitialization:
    """Test provider initialization."""

    def test_get_linkedin_provider(self, scheduler):
        """Test that LinkedIn provider can be initialized."""
        with patch('socialcli.providers.linkedin.provider.LinkedInProvider') as mock_provider:
            provider = scheduler._get_provider('linkedin')
            mock_provider.assert_called_once()

    def test_get_unsupported_provider(self, scheduler):
        """Test that unsupported provider raises error."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            scheduler._get_provider('unsupported_platform')


class TestPostExecution:
    """Test scheduled post execution."""

    def test_execute_post_success(self, scheduler, sample_post_file):
        """Test successful post execution."""
        post_data = {
            'id': 1,
            'provider': 'linkedin',
            'file_path': str(sample_post_file),
            'author': '@testuser',
            'publish_at': datetime.now().isoformat()
        }

        # Mock the provider
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'url': 'https://linkedin.com/post/123', 'id': '123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            result = scheduler._execute_post(post_data)

        assert result is True
        mock_provider.post.assert_called_once()

    def test_execute_post_file_not_found(self, scheduler):
        """Test post execution fails when file doesn't exist."""
        post_data = {
            'id': 1,
            'provider': 'linkedin',
            'file_path': '/nonexistent/file.md',
            'author': '@testuser',
            'publish_at': datetime.now().isoformat()
        }

        result = scheduler._execute_post(post_data)
        assert result is False

    def test_execute_post_provider_error(self, scheduler, sample_post_file):
        """Test post execution handles provider errors."""
        post_data = {
            'id': 1,
            'provider': 'linkedin',
            'file_path': str(sample_post_file),
            'author': '@testuser',
            'publish_at': datetime.now().isoformat()
        }

        # Mock provider that raises error
        mock_provider = MagicMock()
        mock_provider.post.side_effect = Exception("API Error")

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            result = scheduler._execute_post(post_data)

        assert result is False


class TestPendingPostProcessing:
    """Test processing of pending posts."""

    def test_process_no_pending_posts(self, scheduler):
        """Test processing when there are no pending posts."""
        # Should not raise any errors
        scheduler._process_pending_posts()

    def test_process_posts_not_yet_due(self, scheduler, sample_post_file):
        """Test that posts not yet due are not processed."""
        # Schedule a post for the future
        future_time = datetime.now() + timedelta(hours=1)
        scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=future_time.isoformat(),
            status='pending'
        )

        # Mock the execute method to track if it's called
        with patch.object(scheduler, '_execute_post') as mock_execute:
            scheduler._process_pending_posts()
            mock_execute.assert_not_called()

    def test_process_due_posts(self, scheduler, sample_post_file):
        """Test that due posts are processed."""
        # Schedule a post for the past
        past_time = datetime.now() - timedelta(hours=1)
        post_id = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending'
        )

        # Mock successful execution
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            scheduler._process_pending_posts()

        # Verify post was executed and status updated
        post = scheduler.storage.get_scheduled_post(post_id)
        assert post['status'] == 'published'

    def test_process_failed_post_updates_status(self, scheduler, sample_post_file):
        """Test that failed posts have status updated to 'failed'."""
        # Schedule a post for the past
        past_time = datetime.now() - timedelta(hours=1)
        post_id = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending'
        )

        # Mock failed execution
        mock_provider = MagicMock()
        mock_provider.post.side_effect = Exception("API Error")

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            scheduler._process_pending_posts()

        # Verify status updated to failed
        post = scheduler.storage.get_scheduled_post(post_id)
        assert post['status'] == 'failed'

    def test_process_multiple_due_posts(self, scheduler, sample_post_file):
        """Test processing multiple due posts."""
        # Create multiple scheduled posts
        past_time = datetime.now() - timedelta(hours=1)
        for i in range(3):
            scheduler.storage.create_scheduled_post(
                provider='linkedin',
                author='@testuser',
                file_path=str(sample_post_file),
                publish_at=past_time.isoformat(),
                status='pending'
            )

        # Mock successful execution
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            scheduler._process_pending_posts()

        # Verify all posts were processed
        assert mock_provider.post.call_count == 3

        # Verify all posts have updated status
        posts = scheduler.storage.get_all_scheduled_posts()
        for post in posts:
            assert post['status'] == 'published'


class TestSchedulerRunOnce:
    """Test single execution of scheduler."""

    def test_run_once(self, scheduler, sample_post_file):
        """Test run_once processes pending posts."""
        # Schedule a post for the past
        past_time = datetime.now() - timedelta(hours=1)
        scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending'
        )

        # Mock successful execution
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            scheduler.run_once()

        # Verify post was processed
        posts = scheduler.storage.get_all_scheduled_posts()
        assert len(posts) == 1
        assert posts[0]['status'] == 'published'


class TestSchedulerDaemon:
    """Test continuous scheduler daemon execution."""

    def test_run_sets_running_flag(self, scheduler):
        """Test that run() sets the running flag."""
        # Mock sleep to avoid actual waiting
        with patch('time.sleep') as mock_sleep:
            # Stop after first iteration
            mock_sleep.side_effect = lambda x: setattr(scheduler, 'running', False)

            scheduler.run()

            # Should have been set to True initially
            assert mock_sleep.called

    def test_signal_handler_stops_daemon(self, scheduler):
        """Test that signal handler stops the daemon."""
        scheduler.running = True
        scheduler._signal_handler(None, None)
        assert scheduler.running is False
