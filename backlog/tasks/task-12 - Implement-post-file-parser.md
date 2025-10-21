---
id: task-12
title: Implement post file parser
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 21:19'
updated_date: '2025-10-21 08:49'
labels:
  - backend
  - parsing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build the parser that reads markdown and text post files, extracts front matter metadata, and prepares content for posting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Markdown and text file parsing implemented for post content
- [x] #2 YAML front matter extraction works (title, tags, provider, schedule fields)
- [x] #3 Content body extracted correctly after front matter section
- [x] #4 Parser handles posts with and without front matter gracefully
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review spec requirements for post file format (markdown, front matter)
2. Research YAML front matter parsing in Python
3. Implement parser for markdown/text files
4. Add YAML front matter extraction (title, tags, provider, schedule)
5. Extract content body after front matter
6. Handle posts with and without front matter gracefully
7. Add validation for parsed data
8. Create comprehensive unit tests
9. Verify all acceptance criteria are met
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented comprehensive post file parser for markdown and text files:

## Parser Features
- Parses both .md and .txt post files
- YAML front matter extraction with regex pattern matching
- Gracefully handles posts with and without front matter
- UTF-8 and unicode content support

## Front Matter Fields Supported
- title: Post title (string)
- tags: Array or comma-separated string
- provider: Target social platform (string)
- schedule: ISO format datetime (YYYY-MM-DDTHH:MM:SS)
- Custom fields accessible via get_metadata_field()

## Content Extraction
- Extracts content body after front matter delimiters (---)
- Strips leading/trailing whitespace
- Preserves markdown formatting and structure
- Handles edge cases: dashes in content, YAML-like text in body

## Validation
- Validates schedule format (ISO datetime)
- Ensures content is not empty
- Comprehensive error messages for invalid input
- FileNotFoundError for missing files
- ValueError for invalid YAML or schedule format

## Additional Methods
- has_front_matter(): Check if front matter exists
- validate(): Validate parsed data
- to_dict(): Convert to dictionary representation
- get_metadata_field(): Access custom metadata fields

## Testing
- Created 27 comprehensive unit tests covering:
  - Basic parsing (with and without front matter)
  - All front matter field types
  - Content extraction and formatting
  - Validation and error handling
  - Edge cases (unicode, special characters, dashes)
  - Both .md and .txt file types
- All tests passing

## Files Modified
- socialcli/utils/parser.py: Enhanced with validation and utility methods
- tests/utils/test_parser.py: Created comprehensive test suite
<!-- SECTION:NOTES:END -->
