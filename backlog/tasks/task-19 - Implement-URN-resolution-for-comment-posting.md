---
id: task-19
title: Implement URN resolution for comment posting
status: Done
assignee:
  - '@claude'
created_date: '2025-10-22 15:05'
updated_date: '2025-10-22 19:14'
labels:
  - backend
  - scheduler
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When it's time to post a comment, implement the logic to navigate the post-comment relationship, retrieve the URN from the published post, and use it for comment posting. Include proper error handling and logging when URN is unavailable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 URN successfully retrieved from published post via relationship navigation
- [x] #2 Comment posting uses resolved URN from parent post
- [x] #3 Fails gracefully with descriptive error message when URN unavailable
- [x] #4 Error logged with sufficient detail for debugging (post ID, scheduled time, reason)
- [x] #5 Unit tests cover both success and failure scenarios
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update _execute_post() to store URN after successful posting:
   - Extract URN from provider.post() result['id']
   - Call storage.update_scheduled_post(post_id, urn=urn)
   - Ensures URN available for comment resolution

2. Implement _execute_comment() method (replace stub):
   a. Validate parent URN exists:
      - Get parent_data.get('urn')
      - If None/empty: fail with blocked_reason, log error, return False
   
   b. Parse comment file:
      - Check file exists
      - Use PostParser to extract content
      - Handle parse errors gracefully
   
   c. Initialize provider and post comment:
      - Get provider via _get_provider()
      - Call provider.comment(parent_urn, comment_text)
      - Handle authentication and API errors
   
   d. Store comment URN:
      - Extract result['id'] from response
      - Update storage with comment URN
   
   e. Comprehensive error handling:
      - Catch and log all exception types
      - Log with required details (AC4): comment ID, parent ID, scheduled time, reason
      - Update blocked_reason for failed comments

3. Write comprehensive unit tests:
   - Test URN storage in _execute_post
   - Test successful comment posting
   - Test failure when parent URN missing
   - Test failure when comment file not found
   - Test failure when provider raises exception
   - Verify error logging contains all required details

4. Verify all acceptance criteria met
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Successfully implemented URN resolution for comment posting with comprehensive error handling and validation.

### Key Changes

**File: `socialcli/core/scheduler_daemon.py`**

1. **Updated `_execute_post()` to store URN** (lines 153-156):
   - Extracts URN from `provider.post()` result['id']
   - Stores in database via `storage.update_scheduled_post(post_id, urn=urn)`
   - Logs URN storage for debugging
   - **Critical dependency**: Makes URNs available for comment resolution

2. **Implemented `_execute_comment()` method** (lines 283-356):
   - **URN Validation**: Checks parent_data.get('urn') exists, fails gracefully if missing
   - **File Parsing**: Validates file exists, uses PostParser to extract content
   - **Provider Integration**: Calls provider.comment(parent_urn, comment_text)
   - **URN Storage**: Stores comment URN from result['id'] for future reference
   - **Comprehensive Error Handling**:
     - No parent URN → blocked_reason set, detailed error log
     - File not found → return False with logging
     - Provider errors → caught, logged with all required details (AC4)
   - **Error Logging Format** (AC4):
     ```python
     logger.error(
         f"Failed to post comment {comment_id} "
         f"(parent: {parent_id}, scheduled: {scheduled_time}): {error_msg}"
     )
     ```

**File: `tests/core/test_scheduler.py`**

Added comprehensive test suite (`TestCommentPosting` class) with 5 unit tests:

1. **test_execute_post_stores_urn**: Verifies URN storage after successful post
2. **test_execute_comment_success**: Tests full comment posting workflow
   - Verifies provider.comment called with correct URN
   - Verifies comment URN stored
3. **test_execute_comment_fails_when_parent_urn_missing**: Tests graceful failure
   - Verifies blocked_reason set
   - Verifies detailed error logging
4. **test_execute_comment_fails_when_file_not_found**: Tests file validation
5. **test_execute_comment_fails_when_provider_raises_error**: Tests exception handling

### Implementation Details

**URN Resolution Flow**:
1. Parent post published → `_execute_post()` stores URN
2. Comment becomes due → `_process_comments()` validates parent published
3. Parent has URN → `_execute_comment()` retrieves it
4. Comment posted using `provider.comment(parent_urn, text)`
5. Comment URN stored for future reference

**Error Handling Matrix**:
- Parent URN missing → blocked_reason: "Parent post {id} has no URN available"
- File not found → Return False, log error
- Parse error → Caught by try-except, logged
- Provider error → Caught, logged with AC4 details, return False

### All Acceptance Criteria Met
- ✅ AC1: URN retrieved from parent via storage relationship
- ✅ AC2: Comment posting uses provider.comment(urn, text)
- ✅ AC3: Graceful failure with descriptive blocked_reason
- ✅ AC4: Error logging includes post ID, scheduled time, reason
- ✅ AC5: 5 unit tests cover success and failure scenarios

### Testing
All 5 unit tests pass successfully:
```
pytest tests/core/test_scheduler.py::TestCommentPosting -v
5 passed in 0.09s
```

### Integration with Task 18
Task 18 provided the framework (validation, deferral), Task 19 completed the implementation (URN resolution, actual posting).
<!-- SECTION:NOTES:END -->
