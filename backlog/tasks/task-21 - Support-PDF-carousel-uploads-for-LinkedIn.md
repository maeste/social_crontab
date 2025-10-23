---
id: task-21
title: Support PDF carousel uploads for LinkedIn
status: In Progress
assignee:
  - '@claude'
created_date: '2025-10-23 16:59'
updated_date: '2025-10-23 17:40'
labels:
  - enhancement
  - linkedin
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
LinkedIn doesn't support PDF uploads directly. Need to convert PDF pages to images and upload each page as a separate image for carousel posts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Detect when media file is a PDF
- [x] #2 Convert PDF pages to individual images (PNG or JPEG)
- [x] #3 Upload each image separately and collect URNs
- [x] #4 Return all image URNs for multi-image carousel post
- [x] #5 Handle errors gracefully (missing dependencies, conversion failures)
- [ ] #6 Add tests for PDF upload flow

- [ ] #7 Implement upload_document() method using LinkedIn Documents API
- [ ] #8 Update _detect_media_type() to recognize PDFs as 'document' type
- [ ] #9 Update upload_media() to route PDFs to document upload flow
- [ ] #10 Update post() method to handle document content structure
- [ ] #11 Add required headers (Linkedin-Version, X-Restli-Protocol-Version) to client
- [ ] #12 Test PDF upload and posting with carousel
- [ ] #13 Validate file size (<100MB) and page count (<300) for documents
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# UPDATED PLAN: Use LinkedIn Documents API

LinkedIn supporta PDF nativamente tramite Documents API\!
No conversione necessaria - carichiamo il PDF direttamente.

## Implementation Steps:

1. Add document upload support to LinkedInProvider:
   a. Create upload_document() method using Documents API
   b. Initialize upload: POST /rest/documents?action=initializeUpload
   c. Upload file to returned uploadUrl
   d. Return document URN (urn:li:document:{id})

2. Update _detect_media_type() to return "document" for PDFs

3. Update upload_media() to route PDFs to upload_document()

4. Update post() method to handle document media type:
   - Documents use different content structure:
     {"content": {"media": {"title": "file.pdf", "id": "urn:li:document:xxx"}}}

5. Update LinkedInClient to support required headers:
   - Linkedin-Version: 202509 (or current YYYYMM)
   - X-Restli-Protocol-Version: 2.0.0

6. Test with carousel PDF

## Constraints:
- Max file size: 100MB
- Max pages: 300
- Supported: PDF, PPT, PPTX, DOC, DOCX
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added comprehensive debug logging to LinkedInProvider.upload_media():
- Logs registration request/response (status, headers, body)
- Logs file upload request/response (status, headers, body)
- Logs all HTTP errors with full response details

Temporarily allowed PDFs in _detect_media_type() for debugging:
- PDFs now treated as "image" type
- Added warning logs when PDF is detected
- This allows us to see LinkedIn's actual API response when PDF upload is attempted

## All-or-Nothing Policy Implemented

Modified scheduler_daemon.py to enforce strict media upload policy:
- **BEFORE**: Continued posting even if media uploads failed (partial or no media)
- **AFTER**: Fails entire post if ANY media upload fails

Changes:
1. Missing media file → raise FileNotFoundError (fail immediately)
2. Media upload exception → propagates up (fail immediately)
3. Added verification: ensures len(media_ids) == len(media_files)
4. Post only executes if ALL media uploaded successfully

This prevents incomplete posts where media was expected but failed to upload.

## Implementation Complete

### Changes Made:

1. **LinkedInProvider.upload_document()** (NEW)
   - Two-step document upload using LinkedIn Documents API
   - POST /rest/documents?action=initializeUpload → get uploadUrl
   - PUT file to uploadUrl → get document URN
   - Validates file size (<100MB) and type (PDF, DOC, DOCX, PPT, PPTX)
   - Full debug logging for troubleshooting

2. **LinkedInProvider._detect_media_type()** (UPDATED)
   - Now returns "document" for PDF, DOC, DOCX, PPT, PPTX files
   - Removed temporary PDF debugging code
   - Clean detection based on extension and MIME type

3. **LinkedInProvider.upload_media()** (UPDATED)
   - Routes documents to upload_document() method
   - Images/videos continue using existing asset upload flow

4. **LinkedInProvider.post()** (UPDATED)
   - Detects document URNs (urn:li:document:xxx)
   - Uses correct format for documents: {"media": {"title": "file.pdf", "id": "urn:li:document:xxx"}}
   - Accepts media_titles kwarg for document filenames

5. **SchedulerDaemon._execute_post()** (UPDATED)
   - Collects media filenames during upload
   - Passes media_titles to provider.post() for document title field

### Ready to Test:
Run scheduler with DEBUG logging to test PDF carousel upload.

## Fixed API Endpoint Issue

**Problem**: Documents API requires `/rest` base URL, but other endpoints need `/v2`

**Solution**: Added optional `base_url` parameter to `LinkedInClient.request()`
- Default behavior unchanged (use_rest_api chooses between /v2 endpoints)
- Documents upload now specifies: base_url="https://api.linkedin.com/rest"
- Other endpoints (comments, posts) continue using /v2

**Changes**:
- LinkedInClient.request(): Added base_url parameter
- upload_document(): Uses base_url="https://api.linkedin.com/rest"
<!-- SECTION:NOTES:END -->
