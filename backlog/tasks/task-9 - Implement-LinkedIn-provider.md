---
id: task-9
title: Implement LinkedIn provider
status: To Do
assignee: []
created_date: '2025-10-20 21:19'
labels:
  - provider
  - linkedin
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the LinkedInProvider class that implements the SocialProvider interface, enabling post creation and commenting on LinkedIn.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 LinkedInProvider class implements SocialProvider abstract interface
- [ ] #2 post() method successfully creates posts using /rest/posts endpoint
- [ ] #3 comment() method posts comments using /rest/comments endpoint
- [ ] #4 Provider correctly handles author URN for both personal and organization posts
<!-- AC:END -->
