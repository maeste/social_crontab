---
id: task-10
title: Add media upload support for LinkedIn
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 21:19'
updated_date: '2025-10-21 17:26'
labels:
  - media
  - linkedin
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement image and video upload functionality using LinkedIn's asset registration endpoint, enabling rich media posts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Integration with /rest/assets?action=registerUpload endpoint complete
- [x] #2 Image uploads supported and attached correctly to posts
- [x] #3 Video uploads supported with proper media type handling
- [x] #4 Media URNs correctly referenced in post payloads
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Research LinkedIn asset registration API for both images and videos
2. Enhance upload_media() to detect media type (image vs video)
3. Implement separate registration logic for images (feedshare-image) and videos (feedshare-video)
4. Add video-specific upload handling with proper headers
5. Update post() method to properly handle media URNs in content structure
6. Add comprehensive error handling for different media types
7. Write unit tests for image and video uploads
8. Test integration with post creation
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**Media Upload Support Implementation**

**Summary:**
Implemented comprehensive media upload support for both images and videos using LinkedIn's asset registration API.

**Key Changes:**

1. **Media Type Detection** (provider.py:281-318)
   - Added `_detect_media_type()` helper method
   - Supports images: jpg, jpeg, png, gif, bmp, webp
   - Supports videos: mp4, mov, avi, wmv, flv, webm, mkv
   - Uses MIME type detection with extension fallback
   - Comprehensive error handling for unsupported file types

2. **Enhanced upload_media()** (provider.py:320-411)
   - Automatic recipe selection based on media type
   - Images: urn:li:digitalmediaRecipe:feedshare-image
   - Videos: urn:li:digitalmediaRecipe:feedshare-video
   - Added Content-Length and Content-Type headers
   - Improved error handling with specific exceptions

3. **Improved post() Method** (provider.py:135-146)
   - Enhanced media_ids handling to support both list and single values
   - Better null checking for content parameter
   - Proper media URN attachment to post payload

4. **Comprehensive Test Suite** (test_provider.py:283-490)
   - Tests for image upload flow
   - Tests for video upload flow  
   - Media type detection tests (images, videos, unsupported)
   - Error handling tests (file not found, API failures, HTTP errors)
   - All 27 provider tests passing

**Files Modified:**
- socialcli/providers/linkedin/provider.py
- tests/providers/linkedin/test_provider.py

**Testing:**
- All unit tests passing (27/27)
- Integration with post() method validated
- Error handling verified for all edge cases
<!-- SECTION:NOTES:END -->
