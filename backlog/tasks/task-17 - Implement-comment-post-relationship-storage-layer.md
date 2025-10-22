---
id: task-17
title: Implement comment-post relationship storage layer
status: Done
assignee:
  - '@claude'
created_date: '2025-10-22 15:05'
updated_date: '2025-10-22 15:21'
labels:
  - backend
  - storage
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the storage layer functionality to persist and query comment-post relationships. This includes storing comment metadata with post references, querying comments for a given post, and ensuring relationships persist across application restarts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Storage method implemented to save comment with post reference (ID or path)
- [x] #2 Query method implemented to retrieve all comments for a given post
- [x] #3 Relationship data persists correctly across application restarts
- [x] #4 Unit tests cover storage and retrieval scenarios
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add uuid import and helper methods
   - Import uuid module
   - Add _generate_uuid() helper method
   - Add _ensure_uuid(post) helper for lazy migration

2. Implement lazy migration in _read_scheduled_posts()
   - After loading JSON, iterate through posts
   - Add missing fields: uuid (generate), type ("post"), urn (null), parent_uuid (null), blocked_reason (null)
   - Build UUID index: {uuid: post} for O(1) lookups
   - Store index in self._uuid_index

3. Update create_scheduled_post() signature and implementation
   - Add optional parameters: uuid, type, parent_uuid, urn, blocked_reason
   - Generate UUID if not provided
   - Validate: type must be "post" or "comment"
   - Validate: comments must have parent_uuid, posts must not
   - Set defaults for new fields
   - Update new_post dict with all fields

4. Add get_post_by_uuid(uuid) method
   - Load posts (triggers lazy migration and indexing)
   - Use self._uuid_index for O(1) lookup
   - Return post dict or None

5. Add get_comments_for_post(parent_uuid) method
   - Load all posts
   - Filter where type="comment" and parent_uuid matches
   - Return list of comment dicts

6. Update _write_scheduled_posts() to maintain index
   - After writing, rebuild UUID index
   - Ensures index stays in sync with file changes

7. Add validation helper: validate_comment_scheduling(comment_data, parent_post)
   - Check parent exists
   - Check comment.publish_at >= parent.publish_at + 5 minutes
   - Return (is_valid, error_message)

8. Update update_scheduled_post() to handle new fields
   - Allow updating: urn, blocked_reason, type, parent_uuid
   - Rebuild UUID index after update

9. Add get_pending_comments() method
   - Filter posts where type="comment" and status="pending"
   - Filter where publish_at <= now
   - Return sorted by publish_at

10. Write comprehensive unit tests
    - test_uuid_generation_and_indexing()
    - test_lazy_migration_existing_posts()
    - test_create_post_with_uuid()
    - test_create_comment_with_parent()
    - test_get_post_by_uuid()
    - test_get_comments_for_post()
    - test_validation_rules()
    - test_update_urn_and_blocked_reason()
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Successfully implemented complete storage layer for comment-post relationship tracking.

## Implementation Summary:

**New Fields Added**:
- uuid: Auto-generated stable identifier (or custom)
- type: "post" or "comment" 
- urn: LinkedIn URN (captured after publication)
- parent_uuid: Links comments to parent posts
- blocked_reason: Tracks why comments can't post

**New Methods**:
- get_post_by_uuid(uuid) - O(1) lookup via in-memory index
- get_comments_for_post(parent_uuid) - Get all comments for a post
- get_pending_comments(before_time) - Get comments ready to post

**Key Features**:
- Lazy migration: Existing posts auto-migrated on read
- UUID indexing: O(1) lookups for performance
- Validation: Comprehensive checks at scheduling time
  - Comments require parent_uuid, posts cannot have it
  - Parent must exist
  - Comment must be >= 5 min after parent
  - Type must be "post" or "comment"

**Backward Compatibility**:
- create_scheduled_post() now returns {id, uuid} instead of int
- All existing parameters work unchanged
- Old scheduled_posts.json files auto-migrate

**Test Coverage**: 44 tests passing
- 14 new UUID functionality tests
- 2 lazy migration tests
- 10 comment functionality tests
- All existing tests updated and passing

Ready for Task 18 (scheduler integration).
<!-- SECTION:NOTES:END -->
