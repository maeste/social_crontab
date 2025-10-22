---
id: task-18
title: Update comment scheduling to support pre-publication comments
status: Done
assignee:
  - '@claude'
created_date: '2025-10-22 15:05'
updated_date: '2025-10-22 15:36'
labels:
  - backend
  - scheduler
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the scheduler to allow scheduling comments for posts that haven't been published yet. The scheduler should defer comment posting until after the main post is published, and handle validation appropriately.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Scheduler accepts comments scheduled before their parent post
- [x] #2 Scheduler validates parent post is published before attempting to post comment
- [x] #3 Appropriate logging when comment posting is deferred due to unpublished post
- [x] #4 Integration tests verify comment scheduling workflow
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor _process_pending_posts() method:
   - Split into _process_posts() (existing logic filtered for posts only)
   - Create new _process_comments() for comment handling
   - Main method orchestrates both

2. Implement _process_comments() with parent validation:
   - Use storage.get_pending_comments() to get due comments
   - For each comment:
     a. Get parent post by UUID
     b. Validate parent exists (fail comment if missing)
     c. Check parent status:
        - "published" → proceed to execute comment
        - "failed" → fail comment with blocked_reason
        - "pending" → defer (log and keep as pending)
   - Comprehensive logging for all decisions

3. Add _execute_comment() stub:
   - Placeholder method for Task 19 implementation
   - Logs that comment posting not yet implemented
   - Returns False to indicate not yet executed
   - Satisfies AC2 validation requirement

4. Enhance logging throughout:
   - Deferral: "Deferring comment X - parent Y status: pending"
   - Errors: "Parent post UUID not found for comment X"
   - Info: "Processing N comment(s) due for publishing"

5. Write integration tests:
   - Test comment deferred when parent pending
   - Test comment processed when parent published
   - Test comment failed when parent not found
   - Test comment failed when parent failed
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Successfully updated the scheduler daemon to support pre-publication comment scheduling with proper parent post validation.

### Key Changes

**File: `socialcli/core/scheduler_daemon.py`**

1. **Refactored `_process_pending_posts()`**:
   - Split into separate `_process_posts()` and `_process_comments()` methods
   - Main method now orchestrates both post and comment processing
   - Posts filtered by `type='post'` to avoid processing comments as posts

2. **Implemented `_process_comments()`**:
   - Validates parent post existence (fails comment if parent not found)
   - Checks parent post status before attempting to post:
     - **Published**: Proceeds to execute comment via `_execute_comment()`
     - **Failed**: Fails comment with descriptive blocked_reason
     - **Pending**: Defers comment (logs and keeps as pending for retry)
   - Comprehensive logging for all decision paths

3. **Added `_execute_comment()` stub**:
   - Placeholder method for Task 19 (URN resolution)
   - Currently logs "not yet implemented" and returns False
   - Accepts comment_data and parent_data parameters
   - Validates parent is published before attempting execution

### Logging Examples
- Deferral: `"Deferring comment 42 - parent post 10 not yet published (status: pending)"`
- Error: `"Parent post uuid-123 not found for comment 42"`
- Ready: `"Comment 42 ready to post (parent post 10 published)"`

**File: `tests/core/test_scheduler.py`**

Added comprehensive test suite (`TestCommentScheduling` class) with 6 tests:
1. Comment deferred when parent pending
2. Comment processed when parent published
3. Comment failed when parent not found
4. Comment failed when parent failed
5. Multiple comments processed independently
6. Execute comment stub returns False

### All Acceptance Criteria Met
- ✅ AC1: Scheduler accepts comments (via storage validation)
- ✅ AC2: Validates parent published before posting
- ✅ AC3: Appropriate logging for deferrals
- ✅ AC4: Integration tests verify workflow

### Testing
All 6 integration tests pass successfully:
```
pytest tests/core/test_scheduler.py::TestCommentScheduling -v
6 passed in 0.05s
```

### Next Steps
Task 19 will implement the actual URN resolution and comment posting logic in the `_execute_comment()` method.
<!-- SECTION:NOTES:END -->
