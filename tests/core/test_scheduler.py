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
        result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending'
        )
        post_id = result['id']

        # Mock successful execution
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'id': 'urn:li:share:123', 'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            scheduler._process_pending_posts()

        # Verify post was executed and status updated
        post = scheduler.storage.get_scheduled_post(post_id)
        assert post['status'] == 'published'
        # Verify URN was stored (Task 19)
        assert post['urn'] == 'urn:li:share:123'

    def test_process_failed_post_updates_status(self, scheduler, sample_post_file):
        """Test that failed posts have status updated to 'failed'."""
        # Schedule a post for the past
        past_time = datetime.now() - timedelta(hours=1)
        result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending'
        )
        post_id = result['id']

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


class TestCommentScheduling:
    """Test comment scheduling with parent post validation (Task 18)."""

    @pytest.fixture
    def sample_comment_file(self, tmp_path):
        """Create a sample comment file for testing."""
        post_dir = tmp_path / 'posts'
        post_dir.mkdir(parents=True, exist_ok=True)
        comment_file = post_dir / 'test_comment.md'
        comment_file.write_text("""---
platform: linkedin
visibility: public
---

This is a test comment for scheduler.""", encoding='utf-8')
        return comment_file

    def test_comment_deferred_when_parent_pending(self, scheduler, sample_post_file, sample_comment_file):
        """Test that comments are deferred when parent post is pending."""
        # Create parent post scheduled for the past (but still pending - hasn't been processed yet)
        parent_time = datetime.now() - timedelta(hours=1)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=parent_time.isoformat(),
            status='pending',  # Keep as pending to simulate not yet processed
            post_type='post'
        )
        parent_uuid = parent_result['uuid']

        # Create comment scheduled 10 minutes after parent (respects 5-min delay rule)
        # Comment is due (past current time) but parent is still pending
        comment_time = parent_time + timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_uuid
        )
        comment_id = comment_result['id']

        # Mock provider to prevent actual posting (which would change parent status)
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            # Process posts - parent will be "published" but we'll manually keep it pending
            scheduler._process_posts()
            # Manually set parent back to pending (simulating a scenario where post didn't execute)
            scheduler.storage.update_scheduled_post(parent_result['id'], status='pending')

            # Now process comments
            scheduler._process_comments()

        # Verify comment remains pending (deferred) because parent is still pending
        comment = scheduler.storage.get_scheduled_post(comment_id)
        assert comment['status'] == 'pending', "Comment should remain pending when parent is pending"

    def test_comment_processed_when_parent_published(self, scheduler, sample_post_file, sample_comment_file):
        """Test that comments are processed when parent post is published."""
        # Create parent post and mark as published
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='published',
            post_type='post',
            urn='urn:li:share:123456'  # Simulate published post with URN
        )
        parent_uuid = parent_result['uuid']

        # Create comment scheduled for now
        comment_time = datetime.now() - timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_uuid
        )
        comment_id = comment_result['id']

        # Process pending items (comment execution will fail since stub returns False)
        scheduler._process_pending_posts()

        # Verify comment was attempted (status changed from pending)
        comment = scheduler.storage.get_scheduled_post(comment_id)
        assert comment['status'] == 'failed', "Comment should be attempted when parent is published (stub returns False)"

    def test_comment_failed_when_parent_not_found(self, scheduler, sample_comment_file):
        """Test that comments fail when parent post doesn't exist."""
        # Manually create a comment entry bypassing normal validation
        # to simulate a comment whose parent was deleted
        past_time = datetime.now() - timedelta(minutes=10)
        fake_parent_uuid = 'non-existent-uuid-12345'

        # Read storage data
        data = scheduler.storage._read_scheduled_posts()

        # Manually construct comment entry
        comment_id = max([p['id'] for p in data['posts']], default=0) + 1
        comment_entry = {
            'id': comment_id,
            'uuid': scheduler.storage._generate_uuid(),
            'type': 'comment',
            'provider': 'linkedin',
            'author': '@testuser',
            'file_path': str(sample_comment_file),
            'publish_at': past_time.isoformat(),
            'status': 'pending',
            'urn': None,
            'parent_uuid': fake_parent_uuid,
            'blocked_reason': None,
            'created_at': datetime.now().isoformat()
        }

        data['posts'].append(comment_entry)
        scheduler.storage._write_scheduled_posts(data)

        # Process pending items
        scheduler._process_pending_posts()

        # Verify comment failed
        comment = scheduler.storage.get_scheduled_post(comment_id)
        assert comment['status'] == 'failed'
        assert 'not found' in comment.get('blocked_reason', '').lower()

    def test_comment_failed_when_parent_failed(self, scheduler, sample_post_file, sample_comment_file):
        """Test that comments fail when parent post failed."""
        # Create parent post marked as failed
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='failed',
            post_type='post'
        )
        parent_uuid = parent_result['uuid']

        # Create comment scheduled for now
        comment_time = datetime.now() - timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_uuid
        )
        comment_id = comment_result['id']

        # Process pending items
        scheduler._process_pending_posts()

        # Verify comment failed
        comment = scheduler.storage.get_scheduled_post(comment_id)
        assert comment['status'] == 'failed'
        assert 'failed to publish' in comment.get('blocked_reason', '').lower()

    def test_multiple_comments_processed_independently(self, scheduler, sample_post_file, sample_comment_file):
        """Test that multiple comments are processed independently based on parent status."""
        # Create first parent post - published (already completed)
        parent1_time = datetime.now() - timedelta(hours=2)
        parent1_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=parent1_time.isoformat(),
            status='published',
            post_type='post',
            urn='urn:li:share:111111'
        )

        # Create second parent post - will be kept pending
        parent2_time = datetime.now() - timedelta(hours=1)
        parent2_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=parent2_time.isoformat(),
            status='pending',
            post_type='post'
        )

        # Create comments for both parents
        # Comment 1: Due now (10 mins after parent1 which was 2 hours ago)
        comment1_time = parent1_time + timedelta(minutes=10)
        comment1_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment1_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent1_result['uuid']
        )

        # Comment 2: Due now (10 mins after parent2 which was 1 hour ago)
        comment2_time = parent2_time + timedelta(minutes=10)
        comment2_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment2_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent2_result['uuid']
        )

        # Mock provider for both post and comment methods
        mock_provider = MagicMock()
        mock_provider.post.return_value = {'id': 'urn:li:share:999', 'url': 'https://linkedin.com/post/123'}
        mock_provider.comment.return_value = {'id': 'urn:li:comment:888'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            # Process posts
            scheduler._process_posts()
            # Manually set parent2 back to pending (simulating it wasn't processed)
            scheduler.storage.update_scheduled_post(parent2_result['id'], status='pending')

            # Now process comments
            scheduler._process_comments()

        # Verify comment 1 was posted successfully (parent published with URN)
        comment1 = scheduler.storage.get_scheduled_post(comment1_result['id'])
        assert comment1['status'] == 'published'  # Task 19 implementation

        # Verify comment 2 was deferred (parent pending)
        comment2 = scheduler.storage.get_scheduled_post(comment2_result['id'])
        assert comment2['status'] == 'pending'

class TestCommentPosting:
    """Test comment posting with URN resolution (Task 19)."""

    @pytest.fixture
    def sample_comment_file(self, tmp_path):
        """Create a sample comment file for testing."""
        post_dir = tmp_path / 'posts'
        post_dir.mkdir(parents=True, exist_ok=True)
        comment_file = post_dir / 'test_comment.md'
        comment_file.write_text("""---
platform: linkedin
visibility: public
---

This is a test comment.""", encoding='utf-8')
        return comment_file

    def test_execute_post_stores_urn(self, scheduler, sample_post_file):
        """Test that _execute_post stores URN after successful posting."""
        # Create a scheduled post
        past_time = datetime.now() - timedelta(hours=1)
        post_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='pending',
            post_type='post'
        )
        post_id = post_result['id']

        # Create post data
        post_data = {
            'id': post_id,
            'provider': 'linkedin',
            'file_path': str(sample_post_file),
            'author': '@testuser',
            'publish_at': past_time.isoformat()
        }

        # Mock provider with URN in response
        mock_provider = MagicMock()
        test_urn = 'urn:li:share:987654321'
        mock_provider.post.return_value = {'id': test_urn, 'url': 'https://linkedin.com/post/123'}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            result = scheduler._execute_post(post_data)

        # Verify success
        assert result is True

        # Verify URN was stored
        post = scheduler.storage.get_scheduled_post(post_id)
        assert post['urn'] == test_urn

    def test_execute_comment_success(self, scheduler, sample_post_file, sample_comment_file):
        """Test successful comment posting with URN resolution."""
        # Create parent post with URN
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_post_file),
            publish_at=past_time.isoformat(),
            status='published',
            post_type='post',
            urn='urn:li:share:parent123'
        )

        # Create comment
        comment_time = past_time + timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_result['uuid']
        )

        # Get the stored data
        parent_data = scheduler.storage.get_scheduled_post(parent_result['id'])
        comment_data = scheduler.storage.get_scheduled_post(comment_result['id'])

        # Mock provider comment response
        mock_provider = MagicMock()
        test_comment_urn = 'urn:li:comment:comment123'
        mock_provider.comment.return_value = {'id': test_comment_urn}

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            result = scheduler._execute_comment(comment_data, parent_data)

        # Verify success
        assert result is True

        # Verify provider.comment was called with correct URN
        mock_provider.comment.assert_called_once()
        call_args = mock_provider.comment.call_args
        assert call_args[1]['target_id'] == 'urn:li:share:parent123'
        assert 'This is a test comment' in call_args[1]['text']

        # Verify comment URN was stored
        comment = scheduler.storage.get_scheduled_post(comment_result['id'])
        assert comment['urn'] == test_comment_urn

    def test_execute_comment_fails_when_parent_urn_missing(self, scheduler, sample_comment_file):
        """Test comment posting fails gracefully when parent URN is missing."""
        # Create parent post WITHOUT URN
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path='/tmp/fake_post.md',
            publish_at=past_time.isoformat(),
            status='published',
            post_type='post',
            urn=None  # No URN
        )

        # Create comment
        comment_time = past_time + timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_result['uuid']
        )

        # Get the stored data
        parent_data = scheduler.storage.get_scheduled_post(parent_result['id'])
        comment_data = scheduler.storage.get_scheduled_post(comment_result['id'])

        # Execute comment
        result = scheduler._execute_comment(comment_data, parent_data)

        # Verify failure
        assert result is False

        # Verify blocked_reason was set
        comment = scheduler.storage.get_scheduled_post(comment_result['id'])
        assert comment.get('blocked_reason') is not None
        assert 'no urn' in comment['blocked_reason'].lower()

    def test_execute_comment_fails_when_file_not_found(self, scheduler):
        """Test comment posting fails when comment file doesn't exist."""
        # Create parent post with URN
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path='/tmp/fake_post.md',
            publish_at=past_time.isoformat(),
            status='published',
            post_type='post',
            urn='urn:li:share:parent123'
        )

        # Create comment with non-existent file
        comment_data = {
            'id': 999,
            'provider': 'linkedin',
            'file_path': '/nonexistent/comment.md',
            'publish_at': past_time.isoformat()
        }
        parent_data = scheduler.storage.get_scheduled_post(parent_result['id'])

        # Execute comment
        result = scheduler._execute_comment(comment_data, parent_data)

        # Verify failure
        assert result is False

    def test_execute_comment_fails_when_provider_raises_error(self, scheduler, sample_comment_file):
        """Test comment posting fails gracefully when provider raises an error."""
        # Create parent post with URN
        past_time = datetime.now() - timedelta(hours=2)
        parent_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path='/tmp/fake_post.md',
            publish_at=past_time.isoformat(),
            status='published',
            post_type='post',
            urn='urn:li:share:parent123'
        )

        # Create comment
        comment_time = past_time + timedelta(minutes=10)
        comment_result = scheduler.storage.create_scheduled_post(
            provider='linkedin',
            author='@testuser',
            file_path=str(sample_comment_file),
            publish_at=comment_time.isoformat(),
            status='pending',
            post_type='comment',
            parent_uuid=parent_result['uuid']
        )

        # Get the stored data
        parent_data = scheduler.storage.get_scheduled_post(parent_result['id'])
        comment_data = scheduler.storage.get_scheduled_post(comment_result['id'])

        # Mock provider to raise error
        mock_provider = MagicMock()
        mock_provider.comment.side_effect = Exception("API Error")

        with patch.object(scheduler, '_get_provider', return_value=mock_provider):
            result = scheduler._execute_comment(comment_data, parent_data)

        # Verify failure
        assert result is False
