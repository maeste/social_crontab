---
id: task-16
title: Design comment-post relationship model without URN
status: Done
assignee:
  - '@claude'
created_date: '2025-10-22 15:05'
updated_date: '2025-10-22 15:14'
labels:
  - backend
  - design
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design the data model and relationship tracking approach to link comments to posts before the post has a URN. This includes defining how we identify posts (by ID or file path), how we store the relationship, and how we handle edge cases like deleted posts or failed publications.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Schema defined for storing post-comment relationships without URN
- [x] #2 Approach documented for identifying posts (ID, path, or other identifier)
- [x] #3 Edge cases identified and documented (deleted posts, failed publications, orphaned comments)
- [x] #4 Design reviewed and validated for scalability
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Document Enhanced Storage Schema
   - Add uuid (str, auto-generated via uuid4() if not provided)
   - Add type (str, "post" or "comment", default "post")
   - Add urn (str|null, LinkedIn URN after publication, default null)
   - Add parent_uuid (str|null, for comments to reference parent post, default null)
   - Add blocked_reason (str|null, explanation when comment can't post, default null)
   - Maintain backward compatibility with existing fields (id, provider, author, file_path, publish_at, status, created_at, updated_at)

2. Design Post Identification Strategy
   - Use UUID as stable identifier across entire lifecycle
   - UUID generated at scheduling time (before publication)
   - UUID persists even if file moved/renamed
   - Support custom UUID in post frontmatter (advanced use case)
   - Auto-generate UUID if not provided

3. Define Relationship Model
   - Comments reference parent posts via parent_uuid
   - Parent post must exist at comment scheduling time
   - Parent post can have status \!= "published" when comment scheduled
   - Comment lookup via get_post_by_uuid(parent_uuid)
   - Multiple comments can reference same parent_uuid

4. Document Edge Cases and Handling
   - Post never published: Comment blocked with reason "parent_not_published"
   - Post deleted: Comment blocked with reason "parent_missing"
   - URN not captured: Comment blocked with reason "parent_no_urn"
   - Comment scheduled before post: Validation error at scheduling time
   - Post published manually: Need URN recording mechanism or API fallback
   - File path changes: UUID-based lookup unaffected, only content reading impacted

5. Define Validation Rules
   At scheduling time:
   - parent_uuid must exist in storage
   - comment.publish_at must be >= parent.publish_at + 5 minutes
   - type must be "post" or "comment"
   - Comments must have parent_uuid, posts must not
   
   At posting time (comments):
   - parent_uuid must still exist in storage
   - parent.status must equal "published"
   - parent.urn must not be null
   - If validation fails: set blocked_reason, keep status="pending" for retry

6. Design Migration Strategy
   - No explicit migration required - use lazy migration
   - On load: add missing fields with defaults (uuid=generated, type="post", urn=null, etc.)
   - Save updated structure on next write
   - Existing scheduled posts auto-migrate on first access

7. Document CLI Interface Changes
   - queue --list: Display UUID column
   - Post frontmatter: support uuid, parent_uuid, type fields
   - Example comment frontmatter:
     ---
     type: comment
     parent_uuid: abc-123-def
     schedule: 2024-03-20T14:00:00
     ---

8. Document Performance Optimizations
   - Build UUID index in memory: {uuid: post} for O(1) lookups
   - Cache parent lookups when processing batches of comments
   - Batch URN updates to reduce file I/O
   - Document scaling path: migrate to SQLite if >10k items

9. Define Testing Requirements
   - Unit tests: UUID generation, parent validation, lazy migration
   - Integration tests: post->comment workflow, URN capture, blocking logic
   - Edge case tests: orphaned comments, circular refs, timing validation

10. Create Architecture Documentation
    - Enhanced schema diagram with all fields
    - Relationship model diagram (post -> comments via parent_uuid)
    - Workflow diagrams: post publishing (with URN capture), comment posting (with validation)
    - State machine for comment statuses and blocking reasons
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed comprehensive design analysis using Sequential MCP with 15 reasoning steps and 4 parallel exploration agents.

Key Design Decisions:
- UUID-based post identification (stable across lifecycle)
- Enhanced schema with 5 new fields: uuid, type, urn, parent_uuid, blocked_reason
- Lazy migration strategy (backward compatible)
- Validation at both scheduling and posting time
- Comprehensive edge case handling with blocking mechanism

Deliverables:
- 10-step implementation plan documented in task
- Enhanced storage schema defined
- Post identification strategy: UUID (auto-generated via uuid4())
- Edge cases identified: 8 scenarios with solutions
- Validation rules defined for scheduling and posting
- Performance optimizations: UUID indexing, caching, batch operations
- Testing strategy: unit, integration, and edge case tests

Ready for implementation in Task 17.
<!-- SECTION:NOTES:END -->
