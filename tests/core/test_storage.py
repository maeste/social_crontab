"""Tests for storage and logging functionality."""

import json
import pytest
from pathlib import Path
from datetime import datetime
from socialcli.core.storage import Storage, Logger


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage instance for testing."""
    return Storage(base_path=tmp_path)


@pytest.fixture
def storage_with_posts(temp_storage):
    """Create a storage instance with some test posts."""
    # Create some test posts
    temp_storage.create_scheduled_post(
        provider="linkedin",
        author="@testuser",
        file_path="/path/to/post1.md",
        publish_at="2025-10-15T09:00:00",
        status="pending"
    )
    temp_storage.create_scheduled_post(
        provider="linkedin",
        author="@testuser",
        file_path="/path/to/post2.md",
        publish_at="2025-10-20T14:00:00",
        status="published"
    )
    temp_storage.create_scheduled_post(
        provider="twitter",
        author="@testuser",
        file_path="/path/to/post3.md",
        publish_at="2025-10-25T10:00:00",
        status="published"
    )
    return temp_storage


class TestStorageInitialization:
    """Test storage initialization and directory setup."""

    def test_init_creates_directories(self, temp_storage):
        """Test that initialization creates all required directories."""
        assert temp_storage.posts_dir.exists()
        assert temp_storage.media_dir.exists()
        assert temp_storage.logs_dir.exists()

    def test_init_creates_scheduled_posts_file(self, temp_storage):
        """Test that initialization creates the scheduled posts JSON file."""
        assert temp_storage.scheduled_posts_file.exists()

        # Verify file content
        with open(temp_storage.scheduled_posts_file, 'r') as f:
            data = json.load(f)
        assert 'posts' in data
        assert isinstance(data['posts'], list)
        assert len(data['posts']) == 0

    def test_default_base_path(self):
        """Test that default base path is ~/.socialcli."""
        storage = Storage()
        assert storage.base_path == Path.home() / '.socialcli'


class TestScheduledPostCRUD:
    """Test CRUD operations for scheduled posts."""

    def test_create_scheduled_post(self, temp_storage):
        """Test creating a new scheduled post."""
        post_id = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@john",
            file_path="/posts/example.md",
            publish_at="2025-10-21T09:00:00",
            status="pending"
        )

        assert post_id == 1

        # Verify post was saved
        post = temp_storage.get_scheduled_post(post_id)
        assert post is not None
        assert post['id'] == 1
        assert post['provider'] == "linkedin"
        assert post['author'] == "@john"
        assert post['file_path'] == "/posts/example.md"
        assert post['publish_at'] == "2025-10-21T09:00:00"
        assert post['status'] == "pending"
        assert 'created_at' in post

    def test_create_multiple_posts_auto_increment_id(self, temp_storage):
        """Test that IDs auto-increment when creating multiple posts."""
        id1 = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user1",
            file_path="/post1.md",
            publish_at="2025-10-21T09:00:00"
        )
        id2 = temp_storage.create_scheduled_post(
            provider="twitter",
            author="@user2",
            file_path="/post2.md",
            publish_at="2025-10-21T10:00:00"
        )

        assert id2 == id1 + 1

    def test_get_scheduled_post_not_found(self, temp_storage):
        """Test getting a non-existent post returns None."""
        post = temp_storage.get_scheduled_post(999)
        assert post is None

    def test_get_all_scheduled_posts(self, storage_with_posts):
        """Test getting all scheduled posts."""
        posts = storage_with_posts.get_all_scheduled_posts()
        assert len(posts) == 3

    def test_get_all_scheduled_posts_filter_by_status(self, storage_with_posts):
        """Test filtering posts by status."""
        pending_posts = storage_with_posts.get_all_scheduled_posts(status="pending")
        assert len(pending_posts) == 1
        assert pending_posts[0]['status'] == "pending"

        published_posts = storage_with_posts.get_all_scheduled_posts(status="published")
        assert len(published_posts) == 2
        assert all(p['status'] == "published" for p in published_posts)

    def test_get_all_scheduled_posts_filter_by_provider(self, storage_with_posts):
        """Test filtering posts by provider."""
        linkedin_posts = storage_with_posts.get_all_scheduled_posts(provider="linkedin")
        assert len(linkedin_posts) == 2
        assert all(p['provider'] == "linkedin" for p in linkedin_posts)

        twitter_posts = storage_with_posts.get_all_scheduled_posts(provider="twitter")
        assert len(twitter_posts) == 1
        assert twitter_posts[0]['provider'] == "twitter"

    def test_update_scheduled_post(self, storage_with_posts):
        """Test updating a scheduled post."""
        # Update status
        success = storage_with_posts.update_scheduled_post(1, status="published")
        assert success is True

        # Verify update
        post = storage_with_posts.get_scheduled_post(1)
        assert post['status'] == "published"
        assert 'updated_at' in post

    def test_update_scheduled_post_not_found(self, temp_storage):
        """Test updating a non-existent post returns False."""
        success = temp_storage.update_scheduled_post(999, status="published")
        assert success is False

    def test_delete_scheduled_post(self, storage_with_posts):
        """Test deleting a scheduled post."""
        # Verify post exists
        assert storage_with_posts.get_scheduled_post(1) is not None

        # Delete post
        success = storage_with_posts.delete_scheduled_post(1)
        assert success is True

        # Verify post is gone
        assert storage_with_posts.get_scheduled_post(1) is None
        posts = storage_with_posts.get_all_scheduled_posts()
        assert len(posts) == 2

    def test_delete_scheduled_post_not_found(self, temp_storage):
        """Test deleting a non-existent post returns False."""
        success = temp_storage.delete_scheduled_post(999)
        assert success is False


class TestPruneScheduledPosts:
    """Test pruning functionality for scheduled posts."""

    def test_prune_all_published_posts(self, storage_with_posts):
        """Test pruning all published posts without date filters."""
        pruned = storage_with_posts.prune_scheduled_posts()
        assert pruned == 2

        # Verify only pending post remains
        remaining = storage_with_posts.get_all_scheduled_posts()
        assert len(remaining) == 1
        assert remaining[0]['status'] == "pending"

    def test_prune_posts_before_date(self, storage_with_posts):
        """Test pruning posts published before a specific date."""
        # Prune posts before Oct 22
        pruned = storage_with_posts.prune_scheduled_posts(before="2025-10-22")
        assert pruned == 1

        # Verify only the Oct 25 post (and pending post) remain
        remaining = storage_with_posts.get_all_scheduled_posts()
        assert len(remaining) == 2

    def test_prune_posts_after_date(self, storage_with_posts):
        """Test pruning posts published after a specific date."""
        # Prune posts after Oct 19
        pruned = storage_with_posts.prune_scheduled_posts(after="2025-10-19")
        assert pruned == 2

        # Verify only pending post remains
        remaining = storage_with_posts.get_all_scheduled_posts()
        assert len(remaining) == 1
        assert remaining[0]['status'] == "pending"

    def test_prune_posts_date_range(self, storage_with_posts):
        """Test pruning posts within a date range."""
        # Prune posts between Oct 19 and Oct 22
        pruned = storage_with_posts.prune_scheduled_posts(
            after="2025-10-19",
            before="2025-10-22"
        )
        assert pruned == 1

        # Verify two posts remain
        remaining = storage_with_posts.get_all_scheduled_posts()
        assert len(remaining) == 2

    def test_prune_respects_status_filter(self, storage_with_posts):
        """Test that pruning only affects posts with specified status."""
        # Try to prune pending posts (should find 1 pending post)
        pruned = storage_with_posts.prune_scheduled_posts(status="pending")
        assert pruned == 1

        # Only published posts should remain
        all_posts = storage_with_posts.get_all_scheduled_posts()
        assert len(all_posts) == 2
        assert all(p['status'] == 'published' for p in all_posts)

    def test_prune_no_matching_posts(self, storage_with_posts):
        """Test pruning when no posts match criteria."""
        # Try to prune posts before a very early date
        pruned = storage_with_posts.prune_scheduled_posts(before="2020-01-01")
        assert pruned == 0

        # All posts should still exist
        all_posts = storage_with_posts.get_all_scheduled_posts()
        assert len(all_posts) == 3


class TestFileLocking:
    """Test file locking mechanism for concurrent access."""

    def test_concurrent_read_allowed(self, storage_with_posts):
        """Test that multiple concurrent reads are allowed."""
        # This is a basic test - file locking with shared locks allows concurrent reads
        posts1 = storage_with_posts.get_all_scheduled_posts()
        posts2 = storage_with_posts.get_all_scheduled_posts()
        assert posts1 == posts2

    def test_write_updates_file(self, temp_storage):
        """Test that writes properly update the JSON file."""
        post_id = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@test",
            file_path="/test.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Read file directly to verify
        with open(temp_storage.scheduled_posts_file, 'r') as f:
            data = json.load(f)

        assert len(data['posts']) == 1
        assert data['posts'][0]['id'] == post_id


class TestPostStorage:
    """Test post file storage functionality."""

    def test_save_post(self, temp_storage):
        """Test saving post content."""
        content = "# Test Post\n\nThis is a test post."
        file_path = temp_storage.save_post(content, "test.md")

        assert file_path.exists()
        assert file_path.read_text(encoding='utf-8') == content

    def test_get_post(self, temp_storage):
        """Test retrieving post content."""
        content = "# Another Post\n\nContent here."
        temp_storage.save_post(content, "another.md")

        retrieved = temp_storage.get_post("another.md")
        assert retrieved == content

    def test_get_post_not_found(self, temp_storage):
        """Test retrieving non-existent post raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            temp_storage.get_post("nonexistent.md")


class TestMediaStorage:
    """Test media file storage functionality."""

    def test_save_media(self, temp_storage):
        """Test saving media files."""
        media_data = b"fake image data"
        file_path = temp_storage.save_media(media_data, "image.jpg")

        assert file_path.exists()
        assert file_path.read_bytes() == media_data


class TestLogger:
    """Test logging functionality."""

    def test_logger_initialization(self, tmp_path):
        """Test logger initialization creates log file."""
        logger = Logger(log_dir=tmp_path)
        assert logger.log_file.exists()

    def test_get_logger(self, tmp_path):
        """Test getting a logger instance."""
        logger_manager = Logger(log_dir=tmp_path)
        logger = logger_manager.get_logger("test")

        assert logger.name == "test"

    def test_default_log_dir(self):
        """Test that default log directory is ~/.socialcli/logs."""
        logger = Logger()
        assert logger.log_file.parent == Path.home() / '.socialcli' / 'logs'
