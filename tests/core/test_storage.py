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
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@john",
            file_path="/posts/example.md",
            publish_at="2025-10-21T09:00:00",
            status="pending"
        )

        assert 'id' in result
        assert 'uuid' in result
        assert result['id'] == 1

        # Verify post was saved
        post = temp_storage.get_scheduled_post(result['id'])
        assert post is not None
        assert post['id'] == 1
        assert post['provider'] == "linkedin"
        assert post['author'] == "@john"
        assert post['file_path'] == "/posts/example.md"
        assert post['publish_at'] == "2025-10-21T09:00:00"
        assert post['status'] == "pending"
        assert 'created_at' in post
        assert 'uuid' in post

    def test_create_multiple_posts_auto_increment_id(self, temp_storage):
        """Test that IDs auto-increment when creating multiple posts."""
        result1 = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user1",
            file_path="/post1.md",
            publish_at="2025-10-21T09:00:00"
        )
        result2 = temp_storage.create_scheduled_post(
            provider="twitter",
            author="@user2",
            file_path="/post2.md",
            publish_at="2025-10-21T10:00:00"
        )

        assert result2['id'] == result1['id'] + 1

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
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@test",
            file_path="/test.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Read file directly to verify
        with open(temp_storage.scheduled_posts_file, 'r') as f:
            data = json.load(f)

        assert len(data['posts']) == 1
        assert data['posts'][0]['id'] == result['id']


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


class TestUUIDFunctionality:
    """Test UUID generation, indexing, and lookup functionality."""

    def test_create_post_with_auto_generated_uuid(self, temp_storage):
        """Test that posts get auto-generated UUIDs."""
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/test.md",
            publish_at="2025-10-21T09:00:00"
        )

        assert 'uuid' in result
        assert 'id' in result
        assert isinstance(result['uuid'], str)
        assert len(result['uuid']) == 36  # Standard UUID format

        # Verify post has UUID
        post = temp_storage.get_scheduled_post(result['id'])
        assert post['uuid'] == result['uuid']

    def test_create_post_with_custom_uuid(self, temp_storage):
        """Test creating post with custom UUID."""
        custom_uuid = "my-custom-uuid-123"
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/test.md",
            publish_at="2025-10-21T09:00:00",
            uuid_str=custom_uuid
        )

        assert result['uuid'] == custom_uuid

    def test_get_post_by_uuid(self, temp_storage):
        """Test retrieving post by UUID."""
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/test.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Lookup by UUID
        post = temp_storage.get_post_by_uuid(result['uuid'])
        assert post is not None
        assert post['id'] == result['id']
        assert post['uuid'] == result['uuid']

    def test_get_post_by_uuid_not_found(self, temp_storage):
        """Test getting post by non-existent UUID returns None."""
        post = temp_storage.get_post_by_uuid("nonexistent-uuid")
        assert post is None

    def test_uuid_index_performance(self, temp_storage):
        """Test that UUID index provides O(1) lookup."""
        # Create multiple posts
        uuids = []
        for i in range(10):
            result = temp_storage.create_scheduled_post(
                provider="linkedin",
                author=f"@user{i}",
                file_path=f"/post{i}.md",
                publish_at=f"2025-10-{i+15:02d}T09:00:00"
            )
            uuids.append(result['uuid'])

        # All UUIDs should be in index
        assert len(temp_storage._uuid_index) == 10

        # Verify each can be looked up
        for uuid_str in uuids:
            post = temp_storage.get_post_by_uuid(uuid_str)
            assert post is not None
            assert post['uuid'] == uuid_str


class TestLazyMigration:
    """Test lazy migration of existing posts to new schema."""

    def test_lazy_migration_adds_missing_fields(self, temp_storage):
        """Test that lazy migration adds missing fields to old posts."""
        # Manually create old-format post
        data = {'posts': [{
            'id': 1,
            'provider': 'linkedin',
            'author': '@user',
            'file_path': '/test.md',
            'publish_at': '2025-10-21T09:00:00',
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }]}

        # Write old format
        temp_storage._write_scheduled_posts(data)

        # Read triggers migration
        post = temp_storage.get_scheduled_post(1)

        # Verify all new fields exist
        assert 'uuid' in post
        assert 'type' in post
        assert post['type'] == 'post'
        assert 'urn' in post
        assert post['urn'] is None
        assert 'parent_uuid' in post
        assert post['parent_uuid'] is None
        assert 'blocked_reason' in post
        assert post['blocked_reason'] is None

    def test_lazy_migration_preserves_existing_data(self, temp_storage):
        """Test that migration preserves original post data."""
        # Create old-format post with all original fields
        original = {
            'id': 1,
            'provider': 'linkedin',
            'author': '@testuser',
            'file_path': '/important.md',
            'publish_at': '2025-10-21T14:30:00',
            'status': 'published',
            'created_at': '2025-10-01T10:00:00'
        }

        data = {'posts': [original.copy()]}
        temp_storage._write_scheduled_posts(data)

        # Read triggers migration
        post = temp_storage.get_scheduled_post(1)

        # Verify original data preserved
        for key, value in original.items():
            assert post[key] == value


class TestCommentFunctionality:
    """Test comment creation and relationship functionality."""

    def test_create_post_and_comment(self, temp_storage):
        """Test creating a comment linked to a parent post."""
        # Create parent post
        post_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00",
            post_type="post"
        )

        # Create comment
        comment_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/comment.md",
            publish_at="2025-10-21T09:10:00",  # 10 min after post
            post_type="comment",
            parent_uuid=post_result['uuid']
        )

        # Verify comment
        comment = temp_storage.get_scheduled_post(comment_result['id'])
        assert comment['type'] == 'comment'
        assert comment['parent_uuid'] == post_result['uuid']

    def test_create_comment_validation_requires_parent(self, temp_storage):
        """Test that comments must have parent_uuid."""
        with pytest.raises(ValueError, match="Comments must have a parent_uuid"):
            temp_storage.create_scheduled_post(
                provider="linkedin",
                author="@user",
                file_path="/comment.md",
                publish_at="2025-10-21T09:00:00",
                post_type="comment"
                # Missing parent_uuid
            )

    def test_create_post_validation_cannot_have_parent(self, temp_storage):
        """Test that posts cannot have parent_uuid."""
        with pytest.raises(ValueError, match="Posts cannot have a parent_uuid"):
            temp_storage.create_scheduled_post(
                provider="linkedin",
                author="@user",
                file_path="/post.md",
                publish_at="2025-10-21T09:00:00",
                post_type="post",
                parent_uuid="some-uuid"  # Posts can't have parent
            )

    def test_create_comment_validation_parent_exists(self, temp_storage):
        """Test that parent post must exist."""
        with pytest.raises(ValueError, match="Parent post with UUID .* not found"):
            temp_storage.create_scheduled_post(
                provider="linkedin",
                author="@user",
                file_path="/comment.md",
                publish_at="2025-10-21T09:00:00",
                post_type="comment",
                parent_uuid="nonexistent-uuid"
            )

    def test_create_comment_validation_timing(self, temp_storage):
        """Test that comment must be scheduled >= 5 min after parent."""
        # Create parent
        post_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Try to create comment too soon (only 2 min later)
        with pytest.raises(ValueError, match="at least 5 minutes after parent post"):
            temp_storage.create_scheduled_post(
                provider="linkedin",
                author="@user",
                file_path="/comment.md",
                publish_at="2025-10-21T09:02:00",  # Only 2 min later
                post_type="comment",
                parent_uuid=post_result['uuid']
            )

    def test_get_comments_for_post(self, temp_storage):
        """Test retrieving all comments for a post."""
        # Create parent post
        post_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Create multiple comments
        for i in range(3):
            temp_storage.create_scheduled_post(
                provider="linkedin",
                author="@user",
                file_path=f"/comment{i}.md",
                publish_at=f"2025-10-21T09:{10+i*5:02d}:00",
                post_type="comment",
                parent_uuid=post_result['uuid']
            )

        # Get all comments for post
        comments = temp_storage.get_comments_for_post(post_result['uuid'])
        assert len(comments) == 3
        assert all(c['type'] == 'comment' for c in comments)
        assert all(c['parent_uuid'] == post_result['uuid'] for c in comments)

    def test_get_pending_comments(self, temp_storage):
        """Test getting pending comments ready to post."""
        # Create parent post
        post_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Create comments with different statuses and times
        temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/comment1.md",
            publish_at="2025-10-21T09:10:00",
            post_type="comment",
            parent_uuid=post_result['uuid'],
            status="pending"
        )

        temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/comment2.md",
            publish_at="2025-10-21T10:00:00",
            post_type="comment",
            parent_uuid=post_result['uuid'],
            status="published"  # Already published
        )

        # Get pending comments before 9:30
        pending = temp_storage.get_pending_comments(before_time="2025-10-21T09:30:00")
        assert len(pending) == 1
        assert pending[0]['file_path'] == "/comment1.md"
        assert pending[0]['status'] == "pending"

    def test_update_post_with_urn(self, temp_storage):
        """Test updating post with URN after publication."""
        # Create post
        result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00"
        )

        # Simulate publication - update with URN
        test_urn = "urn:li:share:1234567890"
        temp_storage.update_scheduled_post(
            result['id'],
            status="published",
            urn=test_urn
        )

        # Verify URN stored
        post = temp_storage.get_scheduled_post(result['id'])
        assert post['urn'] == test_urn
        assert post['status'] == "published"

    def test_update_comment_with_blocked_reason(self, temp_storage):
        """Test updating comment with blocked_reason."""
        # Create post and comment
        post_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/post.md",
            publish_at="2025-10-21T09:00:00"
        )

        comment_result = temp_storage.create_scheduled_post(
            provider="linkedin",
            author="@user",
            file_path="/comment.md",
            publish_at="2025-10-21T09:10:00",
            post_type="comment",
            parent_uuid=post_result['uuid']
        )

        # Simulate blocking
        temp_storage.update_scheduled_post(
            comment_result['id'],
            blocked_reason="parent_not_published"
        )

        # Verify blocked reason stored
        comment = temp_storage.get_scheduled_post(comment_result['id'])
        assert comment['blocked_reason'] == "parent_not_published"
