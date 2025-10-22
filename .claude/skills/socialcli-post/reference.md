# SocialCLI Post Reference Guide

## Content Writing Frameworks

### Hook Formulas (First 1-2 Lines)

**Problem Statement**:
- "Most [audience] fail at [task] because [reason]."
- "[Shocking statistic] of [audience] struggle with [problem]."
- "Here's why your [approach] isn't working."

**Curiosity Gap**:
- "After [time/experience], I finally discovered [insight]."
- "This changed everything I knew about [topic]."
- "Nobody talks about this, but [controversial truth]."

**Bold Statement**:
- "[Common belief] is wrong. Here's why."
- "Stop [common practice]. Do this instead."
- "The best [solution] isn't what you think."

**Story Opening**:
- "Three years ago, I [situation]. Today, [transformation]."
- "I made a mistake that cost [consequence]."
- "Last week, something happened that changed [outcome]."

**Question Hook**:
- "What if [assumption] was completely wrong?"
- "Why do [percentage] of [audience] fail at [task]?"
- "Have you ever wondered why [phenomenon]?"

### Post Structure Templates

**Educational Post (Tutorial/Insight)**:
```
[Hook: Bold statement or problem]

[Personal context or credential]

[Main content in bullet points or short paragraphs]:
→ Point 1
→ Point 2
→ Point 3

[Key takeaway or lesson learned]

[Call to action: Question or request for engagement]

#Hashtags
```

**Story Post (Personal Experience)**:
```
[Hook: Story opening]

[Challenge or situation faced]

[What you tried or discovered]

[The turning point or insight]

[Result or current state]

[Lesson for readers]

What's your experience with [topic]?

#Hashtags
```

**Announcement Post**:
```
[Hook: Exciting news with emoji]

[What you're announcing]

[Why it matters or context]

[Details or how to participate]

[Call to action]

#Hashtags
```

**Thought Leadership**:
```
[Hook: Controversial or bold statement]

[Context: Why this matters now]

[Your unique perspective backed by]:
→ Data or research
→ Personal experience
→ Industry observation

[Implications or what this means]

[Question to audience for discussion]

#Hashtags
```

### Writing Best Practices

**Clarity**:
- One idea per sentence
- Short paragraphs (1-3 lines)
- Use simple, direct language
- Avoid jargon unless necessary

**Engagement**:
- Ask questions
- Share vulnerabilities
- Challenge assumptions
- Invite different perspectives

**Readability**:
- Use line breaks generously
- Add white space between sections
- Use bullet points (→, •, ✓)
- Strategic emoji use

**Authenticity**:
- Share real experiences
- Admit mistakes or learnings
- Use your genuine voice
- Provide value, not self-promotion

## Date and Time Formatting

### ISO 8601 Format Examples

**Local Time** (uses system timezone):
```
2025-10-25T09:00:00
2025-12-25T14:30:00
2026-01-01T00:00:00
```

**UTC Time** (append Z):
```
2025-10-25T09:00:00Z
2025-12-25T14:30:00Z
```

**With Timezone Offset**:
```
2025-10-25T09:00:00-05:00  # EST
2025-10-25T09:00:00+01:00  # CET
2025-10-25T09:00:00-08:00  # PST
```

### Date Parsing Helper

When user provides informal dates, convert to ISO 8601:

| User Input | ISO 8601 Conversion |
|------------|-------------------|
| "tomorrow at 9am" | `[next_day]T09:00:00` |
| "next Monday 2pm" | `[monday_date]T14:00:00` |
| "in 3 hours" | `[current_time+3h]` |
| "next week Friday" | `[friday_date]T09:00:00` |

## LinkedIn Post Best Practices

### Optimal Posting Times
- Weekday mornings: 7-9 AM
- Lunch hours: 12-1 PM
- Late afternoon: 5-6 PM
- Avoid weekends for professional content

### Content Structure
1. **Hook** (first 1-2 lines): Grab attention
2. **Value** (middle): Provide insights, story, or information
3. **Call to Action** (end): Engage readers, ask questions
4. **Hashtags** (3-5 recommended): Relevant and specific

### Character Limits
- Optimal: 1,300-2,000 characters
- Maximum: 3,000 characters (truncated with "...see more")
- First 150 characters are crucial (preview text)

## Media Guidelines

### Supported Formats
- **Images**: JPG, PNG (recommended: 1200x627px)
- **Max file size**: 10 MB per image
- **Multiple images**: Up to 9 images per post

### Media Best Practices
- Use high-quality, relevant images
- Include alt text for accessibility
- Avoid text-heavy images
- Ensure proper permissions/licensing

## Common Use Cases

### 1. Blog Post Promotion
```markdown
---
platform: linkedin
visibility: public
tags: [blog, content]
---

📝 New blog post: [Title]

[Brief summary highlighting key takeaways]

[Link to blog]

What are your thoughts on [topic]?

#Blogging #[RelevantHashtags]
```

### 2. Project Announcement
```markdown
---
platform: linkedin
visibility: public
media:
  - /path/to/screenshot.png
tags: [project, announcement]
---

🚀 Excited to announce [Project Name]!

[What it does and why it matters]

[Call to action - try it, contribute, feedback]

[Link if applicable]

#OpenSource #[TechStack] #[Domain]
```

### 3. Event Promotion
```markdown
---
platform: linkedin
visibility: public
schedule: 2025-11-01T08:00:00
tags: [event, speaking]
---

🎤 Join me at [Event Name] on [Date]!

I'll be speaking about [Topic]

[What attendees will learn]

[Registration link]

#[EventHashtag] #[Industry]
```

### 4. Career Update
```markdown
---
platform: linkedin
visibility: connections
tags: [career, personal]
---

📢 [Announcement - new role, milestone, achievement]

[Brief reflection or gratitude]

[Looking forward statement]

#[Relevant] #[Tags]
```

### 5. Industry Insights
```markdown
---
platform: linkedin
visibility: public
tags: [insights, industry]
---

💡 [Interesting observation or trend]

[Explanation with examples]

[Your perspective or analysis]

What do you think? [Engaging question]

#[Industry] #[Topic]
```

## SocialCLI Configuration

### Verify Setup
```bash
# Check if authenticated
socialcli login --provider linkedin

# View configuration
cat ~/.socialcli/config.yaml

# Check scheduled posts
socialcli queue --list

# View logs
tail -f ~/.socialcli/socialcli.log
```

### Scheduler Management
```yaml
# In ~/.socialcli/config.yaml
scheduler:
  check_interval: 60  # Check every 60 seconds
  enabled: true
```

## Workflow Automation

### Batch Post Creation
For creating multiple scheduled posts:

1. Create directory structure: `~/posts/YYYY-MM/`
2. Create posts with scheduled times
3. Queue all at once:
```bash
for file in ~/posts/2025-10/*.md; do
  socialcli post --file "$file"
done
```

### Content Calendar Integration
Maintain a calendar file tracking:
- Post topics and themes
- Scheduled dates
- File paths
- Status (draft, queued, published)

## Troubleshooting

### Common Issues

**Post not queuing**
- Check schedule time is in the future
- Verify YAML syntax (use online validator)
- Ensure scheduler is enabled in config

**Media upload fails**
- Verify file paths are absolute
- Check file exists: `ls -lh /path/to/image`
- Ensure file size < 10 MB
- Validate file format (JPG/PNG)

**Authentication errors**
- Re-authenticate: `socialcli login`
- Check token expiry in config
- Verify LinkedIn app credentials

**Schedule not executing**
- Confirm scheduler daemon is running
- Check system time is correct
- Review logs for errors
- Verify check_interval setting

## Interactive Prompts

### Example Conversation Flow

**User**: "I want to create a LinkedIn post"

**Skill**:
"I'll help you create a LinkedIn post! Let me gather some information:

1. What's the content of your post?"

**User**: [Provides content]

**Skill**:
"Great! Now:

2. Do you want to include any images or media? If yes, please provide the file paths."

**User**: [Yes/No + paths OR No]

**Skill**:
"3. When should this be published?
   - 'now' for immediate posting
   - Or provide date/time (e.g., '2025-10-25 at 9am')"

**User**: [Time preference]

**Skill**:
"4. Who should see this post?
   - 'public' (everyone)
   - 'connections' (only your connections)"

**User**: [Visibility choice]

**Skill**:
"5. Any tags for organization? (optional, comma-separated)"

**User**: [Tags or skip]

**Skill**:
"Perfect! I'll create the post file now.

[Shows generated file content]

Does this look correct? I can make changes if needed."

**User**: [Confirms or requests changes]

**Skill**:
"✅ Post created and queued!

File: ~/posts/linkedin-2025-10-21-title.md
Status: [Queued for YYYY-MM-DD HH:MM | Published immediately]

[If scheduled] Remember: The scheduler daemon will publish this automatically at the scheduled time."

## Advanced Features

### Template System
Create reusable templates in `~/.socialcli/templates/`:

```markdown
# template-announcement.md
---
platform: linkedin
visibility: public
tags: [announcement]
---

🎉 [ANNOUNCEMENT]

[DETAILS]

[CTA]

#[TAGS]
```

### Hashtag Strategy
- **Industry**: #SoftwareEngineering, #DataScience, #DevOps
- **Technology**: #Python, #JavaScript, #Kubernetes
- **Topics**: #AI, #CloudComputing, #Microservices
- **Generic**: #Tech, #Development, #Innovation

Use 3-5 relevant hashtags, mix of:
- 1-2 popular (broad reach)
- 2-3 niche (targeted audience)

### Engagement Optimization
- Ask questions to encourage comments
- Tag relevant people/companies (when appropriate)
- Use emojis strategically (but don't overdo)
- Include calls to action
- Respond to comments promptly

## File Naming Convention

**Posts:**
```
linkedin-YYYY-MM-DD-brief-descriptive-title.md
```

Examples:
```
linkedin-2025-10-21-new-blog-post.md
linkedin-2025-10-25-conference-talk.md
linkedin-2025-11-01-project-launch.md
```

**Comments:**
```
comment-YYYY-MM-DD-HH-MM-parent-title.md
```

Examples:
```
comment-2025-10-25-14-05-python-async.md
comment-2025-10-25-14-30-python-async.md
comment-2025-10-25-16-00-python-async.md
```

Benefits:
- Chronological sorting
- Easy to identify content
- Prevents filename conflicts
- Searchable and organized
- Comments clearly linked to parent post

## Comment Scheduling

### Comment Strategy

Comments can significantly boost post engagement when scheduled strategically:

**Early Comments (5-30 minutes)**:
- Add valuable insights
- Clarify key points
- Encourage discussion
- Quick engagement boost

**Mid-Range Comments (30 min - 2 hours)**:
- Share additional resources
- Answer potential questions
- Add related examples
- Re-boost visibility

**Late Comments (2+ hours)**:
- Call-to-action
- Summary or follow-up
- Next steps
- Event/workshop promotion

### Comment Content Guidelines

**Good Comment Examples**:
```
✅ "Key insight: [Framework] isn't just for large systems. Even small projects benefit from [approach]."

✅ "For those asking about real-world examples, I've found [specific technique] works best when [scenario]."

✅ "Thanks for the engagement! I'm hosting a workshop on [topic] next month. DM me if interested!"
```

**Avoid**:
```
❌ "Great post!"
❌ "Thanks for reading!"
❌ "Bump"
```

### Comment Timing Parser

The skill should parse these formats:

| User Input | Delay in Seconds | Absolute Time Calculation |
|-----------|-----------------|-------------------------|
| "5m" | 300 | post_time + 300s |
| "5 minutes" | 300 | post_time + 300s |
| "30 minutes" | 1800 | post_time + 1800s |
| "1 hour" | 3600 | post_time + 3600s |
| "2h" | 7200 | post_time + 7200s |
| "300s" | 300 | post_time + 300s |
| "300 seconds" | 300 | post_time + 300s |

### Comment File Format

Same as posts, but simpler:
```markdown
---
platform: linkedin
visibility: public
---

[Comment content here - keep it conversational and valuable]
```

### Implementation Notes

Comments are scheduled via Python Storage API:
```python
from socialcli.core.storage import Storage
from datetime import datetime, timedelta

storage = Storage()

# After creating post, get UUID from response
post_result = storage.create_scheduled_post(...)
post_uuid = post_result['uuid']

# Parse user delay input (e.g., "30 minutes")
delay_seconds = parse_delay_input(user_input)  # Custom parser

# Calculate comment publish time
post_time = datetime.fromisoformat(post_publish_at)
comment_time = post_time + timedelta(seconds=delay_seconds)

# Schedule comment
comment_result = storage.create_scheduled_post(
    provider='linkedin',
    author=user_author,
    file_path='/path/to/comment.md',
    publish_at=comment_time.isoformat(),
    status='pending',
    post_type='comment',
    parent_uuid=post_uuid
)
```

### Validation Rules

1. **Minimum Delay**: Comments must be at least 5 minutes (300 seconds) after post
2. **Parent Validation**: Parent post must exist and have valid UUID
3. **File Creation**: Comment markdown file must be created before scheduling
4. **Time Calculation**: Absolute time = post_time + delay_seconds

### Common Comment Scheduling Patterns

**Educational Post Pattern**:
- Comment 1 (5 min): Key takeaway
- Comment 2 (30 min): Additional resources
- Comment 3 (2 hours): Q&A or workshop promotion

**Announcement Pattern**:
- Comment 1 (10 min): More details
- Comment 2 (1 hour): Call to action
- Comment 3 (4 hours): Reminder or thank you

**Thought Leadership Pattern**:
- Comment 1 (15 min): Supporting evidence
- Comment 2 (1 hour): Counter-argument addressed
- Comment 3 (3 hours): Summary and next topic teaser
