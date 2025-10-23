# Marp LinkedIn Carousel Creator Skill

A comprehensive skill for creating professional LinkedIn carousel presentations using Marp (Markdown Presentation Ecosystem).

## Overview

This skill guides you through the complete process of creating engaging LinkedIn carousels:

1. **Content Gathering** - Collect your ideas and messages
2. **Slide Optimization** - Structure content for maximum impact
3. **Visual Design** - Choose themes and backgrounds
4. **PDF Generation** - Create publication-ready files
5. **LinkedIn Upload** - Get ready to share with your network

## Quick Start

### Activate the Skill

Simply tell Claude:
- "I want to create a LinkedIn carousel"
- "Help me make a presentation"
- "Create a carousel about [topic]"

The skill will automatically activate and guide you through the process.

## What the Skill Does

### Phase 1: Content Discovery
- Asks for your carousel content/topic
- Understands your target audience
- Identifies the purpose and tone

### Phase 2: Slide Structure
- Asks how many slides you want (recommends 5-10)
- Optimizes content distribution across slides
- Creates logical flow: Hook → Content → CTA
- Presents structure for your approval

### Phase 3: Visual Design
- Offers theme selection (default, gaia, uncover)
- Asks about background images (none, single, or per-slide)
- Validates image paths if backgrounds are requested

### Phase 4: File Generation
- Creates Marp markdown file with proper syntax
- Applies your chosen theme and backgrounds
- Saves to recommended location (`~/carousels/`)

### Phase 5: PDF Creation
- Checks for Marp CLI installation
- Generates PDF using `marp` command
- Verifies output and reports success

### Phase 6: Confirmation
- Shows created file paths
- Provides LinkedIn upload tips
- Offers to make changes or create another carousel

## Prerequisites

### Required

**Marp CLI** must be installed. Choose one option:

**Option 1: Install globally (recommended)**
```bash
npm install -g @marp-team/marp-cli
```

**Option 2: Use npx (no installation)**
```bash
npx @marp-team/marp-cli --version
```

### Optional

**Background images** - If you want custom backgrounds:
- Prepare high-quality images (1920x1080 or higher)
- Save to accessible location
- Have absolute paths ready

## Templates

The skill includes 5 ready-to-use templates:

### 1. Tutorial Carousel
**Use for:** Step-by-step guides, how-to content, educational posts

**Structure:**
- Slide 1: Title/Hook
- Slide 2: Why it matters
- Slides 3-N-1: Step-by-step instructions
- Slide N: Results + CTA

**Example:** "How to Build Microservices in 5 Steps"

### 2. Listicle Carousel
**Use for:** Tips, mistakes to avoid, best practices, top X lists

**Structure:**
- Slide 1: Title ([Number] Things...)
- Slides 2-N-1: One item per slide with explanation
- Slide N: Summary + CTA

**Example:** "7 Python Mistakes to Avoid"

### 3. Before/After Carousel
**Use for:** Transformation stories, case studies, success stories

**Structure:**
- Slide 1: Hook
- Slide 2: The problem (before)
- Slides 3-N-2: The solution/journey
- Slide N-1: The result (after)
- Slide N: Key lesson + CTA

**Example:** "How I Scaled to 1M Users"

### 4. Product Launch Carousel
**Use for:** Product announcements, feature showcases, launches

**Structure:**
- Slide 1: Announcement
- Slide 2: The problem it solves
- Slide 3: The solution overview
- Slides 4-6: Key features
- Slide 7: How it works
- Slide 8: Social proof
- Slide 9: CTA

**Example:** "Introducing Our New Analytics Platform"

### 5. Comparison Carousel
**Use for:** Technology comparisons, decision guides, option analysis

**Structure:**
- Slide 1: Title (A vs B)
- Slide 2: Context
- Slides 3-5: Option A (overview, pros, cons)
- Slides 6-8: Option B (overview, pros, cons)
- Slide 9: When to use each
- Slide 10: Recommendation
- Slide 11: CTA

**Example:** "REST vs GraphQL: Which to Choose?"

## Themes

### Default Theme
- **Style:** Clean, professional, minimal
- **Best for:** Corporate content, formal presentations
- **Colors:** White background, dark text
- **Layout:** Traditional, centered

### Gaia Theme
- **Style:** Modern, colorful, bold
- **Best for:** Creative content, vibrant topics
- **Colors:** Gradient backgrounds, white text
- **Layout:** Dynamic, eye-catching

### Uncover Theme
- **Style:** Minimalist, elegant, centered
- **Best for:** Thought leadership, impactful statements
- **Colors:** Clean, high contrast
- **Layout:** Centered text, lots of white space

## Background Options

### No Backgrounds
**Pros:** Clean, professional, fast to create, small file size
**Cons:** Less visual interest
**Best for:** Text-heavy content, technical topics

### Single Background
**Pros:** Consistent brand look, simple to set up
**Cons:** Can be repetitive
**Best for:** Branded content, cohesive aesthetic

### Per-Slide Backgrounds
**Pros:** Maximum visual impact, contextual imagery
**Cons:** More time to prepare, larger file size
**Best for:** Storytelling, product showcases, visual topics

## Example Interaction

```
You: "I want to create a LinkedIn carousel about Python tips"

Claude: "I'll help you create a professional LinkedIn carousel using Marp!
         Let's start:

         1. What content or topic would you like to include in your carousel?"

You: "5 Python tips for beginners - list comprehensions, f-strings, enumerate,
      with statement, and type hints"

Claude: "Great! Now:

         2. How many slides would you like?
            - Recommended: 5-10 slides for LinkedIn
            - Slide 1: Hook/Title
            - Slides 2-N-1: Main content
            - Slide N: Call to action"

You: "7 slides"

Claude: "Perfect! Let me optimize your content for 7 slides. Here's the
         proposed structure:

         Slide 1: 5 Python Tips for Beginners (title)
         Slide 2: Tip 1 - List Comprehensions
         Slide 3: Tip 2 - F-Strings
         Slide 4: Tip 3 - Enumerate
         Slide 5: Tip 4 - With Statement
         Slide 6: Tip 5 - Type Hints
         Slide 7: Call to action (Follow for more)

         Does this structure work for you?"

You: "Yes, looks good!"

Claude: "Excellent! Now for the visual design:

         3. Which theme would you like?
            - **default**: Clean, professional, minimal
            - **gaia**: Modern, colorful, bold
            - **uncover**: Minimalist, elegant, centered"

You: "Default theme"

Claude: "Great choice! One more thing:

         4. Would you like to add background images?
            - **No backgrounds**: Clean, text-only design
            - **Single background**: One image for all slides
            - **Per-slide backgrounds**: Different image for each slide"

You: "No backgrounds"

Claude: "Perfect! Creating your Marp carousel now...

         ✅ Carousel created successfully!

         **Files:**
         - Markdown: ~/carousels/carousel-2025-10-23-python-tips.md
         - PDF: ~/carousels/carousel-2025-10-23-python-tips.pdf
         - Size: 145 KB

         Your carousel is ready to upload to LinkedIn!"
```

## Best Practices

### Content
- **First slide:** Attention-grabbing hook
- **Middle slides:** One clear idea per slide
- **Last slide:** Strong call to action
- **Text amount:** 3-5 bullet points maximum per slide
- **Flow:** Logical progression from start to finish

### Design
- **Fonts:** Large and readable (mobile-friendly)
- **Contrast:** High contrast for readability
- **Consistency:** Same style throughout
- **White space:** Don't overcrowd slides
- **Branding:** Include logo/contact info

### LinkedIn Optimization
- **Length:** 5-10 slides optimal for engagement
- **Format:** Square (1080x1080) or vertical (1080x1350)
- **File size:** Keep under 100MB
- **Caption:** Write engaging post copy
- **Hashtags:** 3-5 relevant hashtags
- **Timing:** Post during peak engagement hours

## Troubleshooting

### Marp CLI Not Found

**Problem:** `marp: command not found`

**Solution 1:** Install globally
```bash
npm install -g @marp-team/marp-cli
```

**Solution 2:** Use npx
```bash
npx @marp-team/marp-cli input.md -o output.pdf
```

### Background Image Not Loading

**Problem:** Background image doesn't appear in PDF

**Solution:**
- Verify file path is absolute
- Check file exists: `ls -lh /path/to/image.jpg`
- Use `--allow-local-files` flag: `marp input.md --allow-local-files -o output.pdf`

### PDF Generation Fails

**Problem:** Error during PDF generation

**Solution:**
- Ensure Chrome/Chromium is installed (required by Marp)
- Check write permissions in output directory
- Verify markdown syntax is correct
- Try with `--verbose` flag for debugging

### Theme Not Applied

**Problem:** Theme doesn't appear in output

**Solution:**
- Verify theme name is correct (default, gaia, uncover)
- Check frontmatter syntax
- Ensure `marp: true` is set in frontmatter

## Files and Directories

```
.claude/skills/marp-carousel/
├── SKILL.md                         # Main skill instructions
├── reference.md                     # Comprehensive reference guide
├── README.md                        # This file
└── templates/                       # Template library
    ├── tutorial-carousel.md         # How-to guide template
    ├── listicle-carousel.md         # Top X list template
    ├── before-after-carousel.md     # Transformation story template
    ├── product-launch-carousel.md   # Product announcement template
    └── comparison-carousel.md       # A vs B comparison template
```

## Tips for Success

1. **Start with a template** - Choose the pattern that fits your content
2. **Keep it simple** - Less is more on slides
3. **Test on mobile** - Most LinkedIn users view on phone
4. **Add value** - Every slide should provide value
5. **Clear CTA** - Tell people what to do next
6. **Consistent branding** - Use your colors/fonts
7. **Preview before posting** - Check PDF looks good
8. **Engage in comments** - Respond to comments on your carousel

## Advanced Features

### Custom Styling
Add CSS in frontmatter for custom design:
```markdown
---
marp: true
style: |
  section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
---
```

### Background Filters
Apply filters to background images:
```markdown
![bg opacity:.5 blur:5px](image.jpg)
```

### Multiple Backgrounds
Split slide with different backgrounds:
```markdown
![bg left](left-image.jpg)
![bg right](right-image.jpg)
```

## Resources

**Marp:**
- Official site: https://marp.app/
- Documentation: https://marpit.marp.app/
- GitHub: https://github.com/marp-team/marp-cli

**LinkedIn:**
- Carousel best practices
- Optimal posting times
- Engagement tips

**Design:**
- Unsplash (free images)
- Pexels (free photos)
- Coolors (color palettes)
- Canva (design inspiration)

## Support

For issues or questions:
1. Check this README
2. Review `reference.md` for detailed syntax
3. Look at templates for examples
4. Ask Claude for help with the skill

## License

This skill is part of the SocialCLI project and follows the same license (Apache 2.0).

---

**Happy carousel creating! 🎨🚀**
