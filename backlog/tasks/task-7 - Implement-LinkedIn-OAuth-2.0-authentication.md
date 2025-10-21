---
id: task-7
title: Implement LinkedIn OAuth 2.0 authentication
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 21:19'
updated_date: '2025-10-21 09:58'
labels:
  - auth
  - linkedin
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build the OAuth 2.0 three-legged authentication flow for LinkedIn, including token acquisition, storage, and automatic refresh capabilities.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 OAuth 2.0 three-legged flow implemented with authorization URL generation
- [x] #2 Access token and refresh token obtained and stored securely in config
- [x] #3 Token refresh mechanism automatically refreshes expired tokens
- [x] #4 Required OAuth scopes (w_member_social, r_liteprofile) properly requested
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review LinkedIn OAuth 2.0 documentation and flow
2. Review current config system for token storage
3. Implement OAuth URL generation with scopes (w_member_social, r_liteprofile)
4. Implement authorization code exchange for access token
5. Add token storage in config (access_token, refresh_token, expires_at)
6. Implement token refresh mechanism
7. Add token validation and expiry checking
8. Create auth.py module in providers/linkedin/
9. Create comprehensive unit tests
10. Verify all acceptance criteria are met
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

### OAuth 2.0 Flow Implementation
- Implemented complete three-legged OAuth 2.0 flow for LinkedIn
- Authorization URL generation with customizable scopes (default: w_member_social, r_liteprofile)
- Authorization code exchange for access tokens
- Token refresh mechanism with automatic expiry detection

### Token Management
- Integrated with Config system using ProviderConfig dataclass
- Tokens stored in YAML config with fields: access_token, refresh_token, token_expiry
- Automatic token refresh when token expires or within 5 minutes of expiry
- Token validation with get_valid_token() method
- Token clearing functionality for logout scenarios

### Testing
- Created 22 comprehensive unit tests covering:
  - OAuth URL generation (default and custom scopes)
  - Authorization code exchange (success and failure cases)
  - Token refresh (success and failure cases)
  - Token storage and retrieval
  - Automatic token refresh on expiry
  - Authentication status checks
  - Token clearing
  - OAuth scope handling
- All tests passing with 100% coverage

### Files Modified
- `socialcli/providers/linkedin/auth.py` - Enhanced with config integration and token lifecycle management
- `tests/providers/test_linkedin_auth.py` - Comprehensive test suite (22 tests)

### Technical Details
- Used requests library for HTTP calls to LinkedIn OAuth endpoints
- Implemented ISO datetime format for token expiry tracking
- Default token expiry: 60 days (5184000 seconds)
- Refresh buffer: 5 minutes before expiry
- Config field names: token_expiry (not expires_at)

Ready for LinkedIn API client integration (task-8).
<!-- SECTION:NOTES:END -->
