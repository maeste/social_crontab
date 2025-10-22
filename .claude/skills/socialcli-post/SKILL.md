---
name: SocialCLI LinkedIn Post Creator
description: Complete LinkedIn post creation experience - from ideation and content writing to formatting and scheduling. Activate when user wants to create, write, or schedule a LinkedIn post.
allowed-tools: [Write, Bash, AskUserQuestion]
---

# SocialCLI LinkedIn Post Creator

This skill provides a complete end-to-end workflow for creating engaging LinkedIn posts, from initial idea to scheduled publication.

## When to Activate

Activate this skill when the user:
- Wants to create a LinkedIn post
- Wants to schedule a social media post
- Mentions posting to LinkedIn
- Asks about creating social media content
- Needs help writing professional content

## Complete Workflow

### Phase 1: Content Discovery & Strategy

**Understand the user's intent and goals:**

1. **Ask about the post purpose:**
   - What's the main topic or message?
   - What type of post? (announcement, insight, question, story, tutorial, etc.)
   - Who's the target audience?
   - What action do you want readers to take?

2. **Gather context:**
   - Any specific points to cover?
   - Links to share (blog, product, event)?
   - Tone preference (professional, casual, inspirational, educational)?
   - Any constraints (length, style, formality)?

### Phase 2: Content Creation & Refinement

**Help craft engaging content following LinkedIn best practices:**

1. **Structure the post:**
   - **Hook** (first 1-2 lines): Attention-grabbing opening
   - **Value** (body): Main content, insights, story, or information
   - **Call to Action** (ending): Engage readers, ask questions
   - **Hashtags** (3-5 recommended): Relevant and specific

2. **Optimize for LinkedIn:**
   - Keep it concise (1,300-2,000 characters optimal)
   - First 150 characters are crucial (preview text)
   - Use line breaks for readability
   - Add emojis strategically (not excessively)
   - Include relevant hashtags

3. **Draft and iterate:**
   - Present draft to user
   - Offer improvements based on:
     * Clarity and engagement
     * Professional tone
     * Call to action strength
     * Hashtag relevance
   - Refine based on user feedback

4. **Content guidelines to follow:**
   - Make first line compelling (people should want to click "see more")
   - Break text into short paragraphs (2-3 lines max)
   - Use storytelling when appropriate
   - Be authentic and valuable
   - End with a question or call to action

### Phase 3: Technical Details

**Once content is finalized, gather technical information:**

1. **Media files**: Whether they want to include images/media and their paths (optional)
2. **Scheduling**: When to publish (now or scheduled date/time) (optional)
3. **Visibility**: Public or connections only (optional, default: public)
4. **Tags**: Organizational tags for the post (optional)

### Phase 4: File Creation & Publishing

Generate a markdown file with the following structure:

```markdown
---
platform: linkedin
visibility: [public|connections]
schedule: [ISO 8601 format if scheduled, omit if posting now]
tags: [tag1, tag2, tag3]
media:
  - /path/to/image1.jpg
  - /path/to/image2.png
---

[Post content text here]
```

**Important formatting rules:**
- Use YAML front matter (between `---` markers)
- Schedule format: ISO 8601 (`YYYY-MM-DDTHH:MM:SS` for local time, add `Z` for UTC, or timezone offset like `-05:00`)
- Media paths must be absolute paths
- Tags are optional but helpful for organization
- Visibility defaults to `public` if not specified

### Phase 5: Save and Execute

1. Save the post file to a logical location (suggest `~/posts/` directory)
2. Use filename format: `linkedin-YYYY-MM-DD-brief-title.md`
3. Execute the socialcli command:
   - For immediate posting: `socialcli post --file <path>`
   - For scheduled posting: `socialcli post --file <path>` (schedule in front matter)

### Phase 6: Confirm Success & Schedule Comments

**Post Confirmation:**
- Show the user the created file path
- Display the socialcli command output
- Confirm whether the post was queued or published
- If scheduled, remind user about the scheduler daemon

**Comment Scheduling (Optional):**

After successfully creating the post, ask if the user wants to schedule comments:

1. **Ask about comments:**
   - "Would you like to schedule one or more comments on this post?"
   - "Comments can help boost engagement and keep the conversation going"

2. **If user wants comments, for each comment:**
   - Ask for the comment text
   - Ask for timing: "How long after the post should this comment be published?"
     * Accept input in seconds (e.g., "300s", "300 seconds") or minutes (e.g., "5m", "5 minutes")
     * Minimum delay: 5 minutes (300 seconds) from post publication time
     * Suggest common delays: 5 minutes, 30 minutes, 1 hour, 2 hours

3. **Create comment files:**
   - Save each comment to `~/posts/comments/` directory
   - Use filename format: `comment-YYYY-MM-DD-HH-MM-parent-title.md`
   - Calculate absolute publish time: post_time + delay
   - Store parent post UUID for linking

4. **Execute comment scheduling:**
   - Use internal storage API (not direct CLI) to schedule comments
   - Each comment needs: provider, author, file_path, publish_at, parent_uuid
   - Confirm successful scheduling for each comment

**Comment File Format:**
```markdown
---
platform: linkedin
visibility: public
---

[Comment content text here]
```

**Important Comment Rules:**
- Comments must be scheduled at least 5 minutes AFTER the parent post
- Comments are linked to parent post via UUID (handled internally)
- Comments require the parent post to be published before they can be posted
- Comments use the same markdown format as posts (with front matter)
- Multiple comments can be scheduled for the same post

**Final Actions:**
- Offer to create another post or make modifications
- Remind about scheduler daemon if any scheduled items exist

## Examples

### Example 1: Simple Text Post (Immediate)
```markdown
---
platform: linkedin
visibility: public
---

💬 Excited to share my latest blog post on microservices architecture!

Learn how to build scalable systems with domain-driven design.

#SoftwareEngineering #Microservices #Architecture
```

Command: `socialcli post --file ~/posts/linkedin-2025-10-21-microservices.md`

### Example 2: Scheduled Post with Image
```markdown
---
platform: linkedin
visibility: public
schedule: 2025-10-25T09:00:00
media:
  - /home/user/images/presentation-slide.png
tags: [speaking, conference]
---

🎤 Looking forward to speaking at DevConf 2025 next week!

Topic: "Building Resilient Distributed Systems"

See you there! 🚀

#DevConf2025 #DistributedSystems
```

Command: `socialcli post --file ~/posts/linkedin-2025-10-21-devconf.md`

### Example 3: Connections-Only Post
```markdown
---
platform: linkedin
visibility: connections
tags: [personal, announcement]
---

📢 Personal update: Starting a new role as Principal Engineer at TechCorp!

Grateful for this opportunity to work on challenging problems.

#CareerUpdate #NewBeginnings
```

Command: `socialcli post --file ~/posts/linkedin-2025-10-21-new-role.md`

### Example 4: Post with Scheduled Comments
**Main Post:**
```markdown
---
platform: linkedin
visibility: public
schedule: 2025-10-25T14:00:00
tags: [tutorial, python]
---

🐍 Just published: Complete Guide to Python Async Programming

Learn how to write efficient async code with practical examples.

Check it out: https://myblog.com/python-async

#Python #AsyncIO #Programming
```

Command: `socialcli post --file ~/posts/linkedin-2025-10-25-python-async.md`

**Scheduled Comments:**

Comment 1 (5 minutes after post - 14:05:00):
```markdown
---
platform: linkedin
visibility: public
---

Key takeaway: async/await isn't just about performance—it's about writing more maintainable concurrent code 🚀
```

Comment 2 (30 minutes after post - 14:30:00):
```markdown
---
platform: linkedin
visibility: public
---

For those asking about real-world examples, I've added a section on using asyncio with web scraping and API calls. Let me know if you want more examples! 💡
```

Comment 3 (2 hours after post - 16:00:00):
```markdown
---
platform: linkedin
visibility: public
---

Thanks for all the engagement! I'm planning a follow-up post on async testing strategies. What topics would you like me to cover? 🤔
```

**Files Created:**
- Post: `~/posts/linkedin-2025-10-25-python-async.md`
- Comment 1: `~/posts/comments/comment-2025-10-25-14-05-python-async.md`
- Comment 2: `~/posts/comments/comment-2025-10-25-14-30-python-async.md`
- Comment 3: `~/posts/comments/comment-2025-10-25-16-00-python-async.md`

**Implementation Notes:**
- Comments are scheduled using Python storage API directly (not CLI)
- Each comment is linked to the parent post via UUID
- Comment timing is calculated as: post_time + user_specified_delay
- All comments are validated to be at least 5 minutes after the post

## Important Notes

1. **Directory Setup**:
   - Suggest creating `~/posts/` directory if it doesn't exist
   - Suggest creating `~/posts/comments/` directory for comment files
2. **Scheduler**: Remind users that scheduled posts require the scheduler daemon to be running
3. **Authentication**: Ensure user has authenticated with `socialcli login` before posting
4. **Media Validation**: Verify media file paths exist before creating the post
5. **ISO 8601 Format**: Help users format dates correctly (YYYY-MM-DDTHH:MM:SS)
6. **Comment Timing**:
   - Comments must be at least 5 minutes after the parent post
   - Parse user input for delays: "5m", "5 minutes", "300s", "300 seconds"
   - Calculate absolute publish time: parent_post_time + delay
7. **Comment Storage**:
   - Comments are scheduled using Python's Storage API
   - Need to extract UUID from post creation response
   - Store parent_uuid, provider, author, file_path, and publish_at

## Error Handling

**Post-related errors:**
- Check if user is authenticated: `socialcli login`
- Verify file paths are correct
- Check front matter YAML syntax
- Ensure schedule time is in the future
- Validate media file paths exist

**Comment-related errors:**
- Ensure comment delay is at least 5 minutes
- Verify parent post was successfully created (has UUID)
- Check comment file creation and content
- Validate comment timing calculations
- Ensure Storage API is accessible for direct scheduling

## Quick Reference: Front Matter Fields

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `platform` | string | Yes | Target platform | linkedin |
| `visibility` | string | No | Post visibility | public |
| `schedule` | datetime | No | When to publish (ISO 8601) | now |
| `tags` | list | No | Organization tags | [] |
| `media` | list | No | Media file paths | [] |

## Complete Interaction Example

### Example: Creating an Educational Post

**User**: "I want to create a LinkedIn post"

**Skill**: "Great! I'll help you create an engaging LinkedIn post. Let's start with understanding what you want to share:

1. What's the main topic or message of your post?
2. What type of post is this? (e.g., announcement, insight, tutorial, question, story)
3. Who's your target audience?
4. What action do you want readers to take?"

**User**: "I want to share insights about microservices architecture. It's educational content for software engineers. I want them to read my blog post."

**Skill**: "Perfect! An educational post about microservices for developers. Do you have:
- Any specific points you want to highlight?
- A link to your blog post?
- Any preferred tone? (professional/casual/inspirational)"

**User**: "I want to highlight domain-driven design and scalability. Here's the link: https://myblog.com/microservices. Professional but approachable tone."

**Skill**: "Excellent! Here's a draft for your post:

---
🏗️ Building Better Microservices with Domain-Driven Design

After working with distributed systems for 5+ years, I've learned that the key to successful microservices isn't just about splitting code—it's about understanding your domain.

In my latest blog post, I explore:
→ How DDD principles guide service boundaries
→ Avoiding the distributed monolith trap
→ Practical patterns for scalable architectures

The biggest lesson? Start with your business domains, not your technology stack.

Read the full article: https://myblog.com/microservices

What's been your biggest challenge with microservices?

#SoftwareEngineering #Microservices #DomainDrivenDesign #Architecture
---

What do you think? Would you like me to adjust the tone, length, or focus?"

**User**: "Looks great! Can you make the hook more attention-grabbing?"

**Skill**: "Absolutely! Here's an updated version with a stronger hook:

---
🏗️ Most microservices fail because teams split the wrong things.

After 5+ years fixing broken distributed systems, I've seen the same mistake repeatedly: teams divide by technology, not by business domain.

The solution? Domain-Driven Design.

In my latest blog post, I break down:
→ How DDD principles guide service boundaries
→ Avoiding the distributed monolith trap
→ Practical patterns for scalable architectures

Read the full article: https://myblog.com/microservices

What's been your biggest microservices challenge?

#SoftwareEngineering #Microservices #DomainDrivenDesign #Architecture
---

Better? Ready to proceed with scheduling?"

**User**: "Perfect! Schedule it for tomorrow at 9 AM"

**Skill**: "Great! A few final details:
1. Do you want to include any images or media?
2. Visibility: public (everyone) or connections only?
3. Any organizational tags for your records?"

**User**: "No images. Public. Tags: blog, education"

**Skill**: "✅ Perfect! Creating your post now...

[Creates file and executes command]

✅ Post created and scheduled!

**File**: ~/posts/linkedin-2025-10-22-microservices-ddd.md
**Scheduled**: 2025-10-22 at 09:00:00
**Status**: Queued for publication
**Post UUID**: abc123-def456-ghi789

Your post will be automatically published tomorrow at 9 AM.

Would you like to schedule one or more comments on this post? Comments can help boost engagement and keep the conversation going."

**User**: "Yes! Let me add 2 comments"

**Skill**: "Great! Let's schedule your comments. Each comment must be at least 5 minutes after the post.

**Comment 1:**
What would you like the first comment to say?"

**User**: "Key insight: DDD isn't just for large systems. Even small projects benefit from clear domain boundaries."

**Skill**: "Excellent point! When should this comment be published?
- Suggested options: 5 minutes, 30 minutes, 1 hour, 2 hours after the post
- Or specify your own: e.g., '10m', '45 minutes', '90 seconds'"

**User**: "30 minutes after"

**Skill**: "✅ Comment 1 scheduled for 2025-10-22 at 09:30:00 (30 minutes after post)

**Comment 2:**
What would you like the second comment to say?"

**User**: "Thanks for the engagement! For those interested, I'm planning a workshop on implementing bounded contexts. DM me if interested!"

**Skill**: "Perfect call-to-action! When should this comment be published?"

**User**: "2 hours after the post"

**Skill**: "✅ Comment 2 scheduled for 2025-10-22 at 11:00:00 (2 hours after post)

[Creates comment files and schedules them via Storage API]

✅ All comments scheduled successfully!

**Summary:**
- **Main Post**: Tomorrow at 09:00:00
- **Comment 1**: Tomorrow at 09:30:00 (30 min after)
- **Comment 2**: Tomorrow at 11:00:00 (2 hours after)

**Files created:**
- ~/posts/linkedin-2025-10-22-microservices-ddd.md
- ~/posts/comments/comment-2025-10-22-09-30-microservices-ddd.md
- ~/posts/comments/comment-2025-10-22-11-00-microservices-ddd.md

Make sure your scheduler daemon is running! Your post and comments will be automatically published at the scheduled times.

Would you like to create another post or make any changes?"

## User Interaction Tips

**General Tips:**
- Be conversational and friendly throughout all phases
- Help craft compelling content, not just format it
- Provide clear examples for date/time formatting
- Suggest improvements based on LinkedIn best practices
- Validate user input before creating files
- Show the generated file content for confirmation
- Offer to iterate on content quality
- Guide users through the complete creative process

**Comment Scheduling Tips:**
- Always ask about comments AFTER successfully scheduling the post
- Explain that comments boost engagement and keep conversations alive
- Help users craft engaging comment content (not just "Great post!")
- Suggest strategic timing: early comments (5-30 min) for quick engagement, later comments (1-2 hours) to re-boost visibility
- Parse timing flexibly: "5m", "5 minutes", "300s", "300 seconds" all work
- Validate minimum 5-minute delay and provide helpful error messages
- Show clear summary of all scheduled items with absolute times
- Remind about the scheduler daemon for both posts and comments
