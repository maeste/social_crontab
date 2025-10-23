---
name: Marp LinkedIn Carousel Creator
description: Create LinkedIn carousel presentations using Marp. Guides through content creation, slide optimization, and PDF generation. Activate when user wants to create a carousel or presentation for LinkedIn.
allowed-tools: [Write, Bash, AskUserQuestion, Read]
---

# Marp LinkedIn Carousel Creator

This skill provides a complete workflow for creating professional LinkedIn carousel presentations using Marp (Markdown Presentation Ecosystem).

## When to Activate

Activate this skill when the user:
- Wants to create a LinkedIn carousel
- Mentions creating a presentation or slides
- Asks about Marp or slide creation
- Needs help formatting content into slides
- Wants to create a PDF carousel for social media

## Complete Workflow

### Phase 1: Content Gathering

**Collect the carousel content:**

1. **Ask for the main content:**
   - "What content would you like to include in your carousel?"
   - "What's the main topic or message?"
   - User can provide:
     * Raw text or outline
     * Bullet points
     * Full paragraphs
     * Key messages

2. **Understand the context:**
   - Target audience (professionals, developers, general public)
   - Purpose (educate, promote, inspire, explain)
   - Tone (professional, casual, technical)

### Phase 2: Slide Structure

**Optimize content for slides:**

1. **Ask about slide count:**
   - "How many slides would you like for this carousel?"
   - Suggest optimal range: 5-10 slides (LinkedIn carousel sweet spot)
   - Explain: First slide = hook, Middle slides = content, Last slide = CTA

2. **Analyze and optimize content:**
   - Break down content into logical sections
   - Create a slide structure:
     * Slide 1: **Title/Hook** - Grab attention
     * Slides 2-N-1: **Content** - Core message, one idea per slide
     * Slide N: **Call to Action** - Next steps, contact, follow

3. **Present optimized structure:**
   - Show user the proposed slide breakdown
   - Example:
     ```
     Slide 1: [Hook/Title]
     Slide 2: [First key point]
     Slide 3: [Second key point]
     ...
     Slide N: [CTA]
     ```
   - Get user confirmation or iterate

4. **Ask about image-only slides (optional):**
   - "Do you want any slides to contain only an image (no text)?"
   - If yes: "Which slide number(s)? For example: 'Slide 3' or 'Slides 3 and 5'"
   - Note these slides for special handling during generation

### Phase 2.5: Format Selection

**Choose LinkedIn carousel format:**

1. **Ask about carousel format:**
   - "Which format would you like for your carousel?"
   - Options:
     * **Square (1080x1080)** - Most versatile, works everywhere, 1:1 aspect ratio
     * **Portrait (1080x1350)** - More vertical space, mobile-optimized, 4:5 aspect ratio
   - Explain: Both work on LinkedIn, square is more common, portrait gives more room

2. **LinkedIn technical specifications:**
   - DPI: 300 (professional quality, minimum 72)
   - Format: PDF/A, PDF 1.4+, or PDF/X
   - Max file size: 100MB
   - Max pages: 300 (recommended: 8-12 for engagement)
   - Mobile-optimized: Content designed for smaller screens

### Phase 3: Visual Design

**Configure visual appearance:**

1. **Ask about theme:**
   - "Which Marp theme would you like?"
   - Options:
     * **default** - Clean, professional, minimal
     * **gaia** - Modern, colorful, bold
     * **uncover** - Minimalist, elegant, centered text
   - Provide brief description of each theme

2. **Ask about backgrounds:**
   - "Would you like to add backgrounds to your slides?"
   - Options:
     * **No backgrounds** - Text-only, clean design, minimal file size
     * **Solid color** - Single color background using CSS (lightweight)
     * **Single image** - One image for all slides
     * **Per-slide images** - Different image for each slide (can skip slides)

3. **If 'Solid color' selected:**
   - Ask: "What color would you like? (hex code, color name, or gradient)"
   - Examples:
     * Hex: `#4A90E2` (blue)
     * Name: `#1a1a1a` (dark), `#f5f5f5` (light)
     * Gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
   - Apply via CSS in frontmatter (lightweight, no images)

4. **If 'Single image' or 'Per-slide images' selected:**
   - Ask for image paths (absolute paths only)
   - **IMPORTANT:** Validate each file exists using bash: `ls -lh /path/to/image.jpg`
   - Show file size and confirm images are accessible
   - Explain background options:
     * `![bg](image.jpg)` - Full background
     * `![bg fit](image.jpg)` - Fit to slide
     * `![bg cover](image.jpg)` - Cover entire slide (default)
     * `![bg left](image.jpg)` - Left half
     * `![bg right](image.jpg)` - Right half
     * `![bg opacity:.3](image.jpg)` - Transparent overlay (good for text readability)

5. **If 'Per-slide images' selected:**
   - For each slide, ask: "Background for Slide X? (provide path or type 'skip' for no background)"
   - Allow user to skip specific slides (no background on those)
   - Track which slides have backgrounds and which don't
   - Example:
     ```
     Slide 1: /path/to/hero.jpg
     Slide 2: skip (no background)
     Slide 3: /path/to/content.jpg
     Slide 4: skip
     Slide 5: /path/to/cta.jpg
     ```

### Phase 4: Marp File Generation

**Create the Marp markdown file:**

1. **Configure frontmatter based on user choices:**

   **Basic frontmatter structure:**
   ```yaml
   ---
   marp: true
   theme: [user-selected-theme]
   paginate: true
   size: [format-choice]
   ---
   ```

   **Size configuration:**
   - If Square (1080x1080): `size: 4:3` or custom `size: 1080px 1080px`
   - If Portrait (1080x1350): `size: 4:5` or custom `size: 1080px 1350px`

   **Background color (if solid color selected):**
   ```yaml
   ---
   marp: true
   theme: [selected-theme]
   paginate: true
   size: [format]
   backgroundColor: [user-color]
   style: |
     section {
       background: [user-color-or-gradient];
     }
   ---
   ```

   **Examples:**
   - Solid color: `backgroundColor: #4A90E2`
   - Gradient: `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`

2. **Build slides with appropriate content:**

   **Standard content slide:**
   ```markdown
   <!-- Slide 2: Content -->
   ## [Heading]

   - Point 1
   - Point 2
   - Point 3

   ---
   ```

   **Image-only slide (if user requested):**
   ```markdown
   <!-- Slide 3: Image Only -->
   ![bg cover](/absolute/path/to/image.jpg)

   ---
   ```
   - No text content
   - Only background image directive
   - Use `cover` to fill entire slide

   **Slide with per-slide background:**
   ```markdown
   <!-- Slide 4: Content with Background -->
   ![bg opacity:.3](/path/to/background.jpg)

   ## [Heading]

   Content here with semi-transparent background

   ---
   ```

   **Slide without background (when per-slide and user said 'skip'):**
   ```markdown
   <!-- Slide 5: No Background -->
   ## [Heading]

   Regular content without background

   ---
   ```

3. **Complete file structure example:**
   ```markdown
   ---
   marp: true
   theme: default
   paginate: true
   size: 1080px 1080px
   ---

   <!-- Slide 1: Title/Hook -->
   ![bg opacity:.2](/path/to/hero.jpg)

   # [Title]

   [Subtitle or tagline]

   ---

   <!-- Slide 2: Content (no background) -->
   ## [Heading]

   - Point 1
   - Point 2
   - Point 3

   ---

   <!-- Slide 3: Image Only -->
   ![bg cover](/path/to/visual.jpg)

   ---

   <!-- Slide 4: Content with background -->
   ![bg opacity:.3](/path/to/bg.jpg)

   ## [Another Point]

   More content

   ---

   <!-- Final Slide: CTA -->
   # [Call to Action]

   [Contact info or next steps]
   ```

4. **Formatting guidelines:**
   - Use proper Markdown syntax
   - One main idea per slide (unless image-only)
   - Keep text concise (3-5 bullet points max per slide)
   - Use headings for structure (# for title, ## for sections)
   - Add descriptive comments for each slide
   - Include proper slide separators (`---`) BETWEEN slides
   - **⚠️ IMPORTANT:** Do NOT add `---` after the last slide (causes empty page)
   - For backgrounds, always use absolute paths
   - For image-only slides, only include background directive

   **Common mistake to avoid:**
   ```markdown
   <!-- Last slide -->
   # Call to Action

   Content here

   ---        ← ❌ REMOVE THIS! Causes empty 5th page
   ```

   **Correct format:**
   ```markdown
   <!-- Last slide -->
   # Call to Action

   Content here
              ← ✅ File ends here, no trailing ---
   ```

5. **Background application rules:**
   - **No backgrounds:** Clean frontmatter, no bg directives
   - **Solid color:** CSS in frontmatter, lightweight
   - **Single image:** Add `![bg](path)` to first slide after frontmatter (applies to all)
   - **Per-slide images:** Add `![bg](path)` to specific slides, skip others
   - **Image-only slides:** Use `![bg cover](path)` with no text content

### Phase 5: PDF Generation

**Generate the PDF using Marp CLI with LinkedIn specifications:**

1. **Save the Marp file:**
   - Suggest location: `~/carousels/` or `~/presentations/`
   - Filename format: `carousel-YYYY-MM-DD-topic.md`
   - Show user the file content for review

2. **Check Marp installation:**
   ```bash
   which marp || npx @marp-team/marp-cli --version
   ```

3. **Generate LinkedIn-optimized PDF:**

   **Standard command (recommended):**
   ```bash
   marp input.md \
     --pdf \
     --allow-local-files \
     --pdf-outlines \
     -o output.pdf
   ```

   **With quality optimization:**
   ```bash
   # For Square format (1080x1080)
   marp input.md \
     --pdf \
     --allow-local-files \
     --pdf-outlines \
     --pdf-notes \
     -o output.pdf

   # For Portrait format (1080x1350)
   marp input.md \
     --pdf \
     --allow-local-files \
     --pdf-outlines \
     -o output.pdf
   ```

   **Using npx (if Marp not installed):**
   ```bash
   npx @marp-team/marp-cli input.md \
     --pdf \
     --allow-local-files \
     --pdf-outlines \
     -o output.pdf
   ```

   **Command flags explained:**
   - `--pdf`: Force PDF output format
   - `--allow-local-files`: Enable local image file access
   - `--pdf-outlines`: Add PDF bookmarks/outlines
   - `--pdf-notes`: Include slide notes in PDF (optional)
   - `-o output.pdf`: Specify output file path

4. **LinkedIn PDF specifications check:**
   After generation, verify:
   - **Format:** PDF/A, PDF 1.4+, or PDF/X ✓
   - **Dimensions:**
     * Square: 1080x1080px (1:1 ratio) ✓
     * Portrait: 1080x1350px (4:5 ratio) ✓
   - **DPI:** 300 for professional quality (Marp default is good)
   - **File size:** Must be under 100MB (check with `ls -lh output.pdf`)
   - **Page count:** Recommended 8-12 pages for engagement, max 300
   - **Mobile-optimized:** Large fonts, high contrast verified

5. **Verify and report:**
   ```bash
   # Check file size
   ls -lh output.pdf

   # IMPORTANT: Verify page count matches expected slides
   pdfinfo output.pdf | grep Pages
   # Expected: Pages:           N (where N = requested slide count)
   # If Pages = N+1, there's a trailing --- in the markdown

   # Open for preview (optional)
   xdg-open output.pdf  # Linux
   open output.pdf      # macOS
   ```

   **If page count is incorrect (N+1):**
   - Check markdown file for trailing `---` after last slide
   - Remove the trailing separator
   - Regenerate PDF
   - Verify page count again

   Report to user:
   - ✅ PDF created successfully
   - File path: `~/carousels/carousel-YYYY-MM-DD-topic.pdf`
   - File size: [size in KB/MB]
   - Format: [Square/Portrait]
   - **Page count: [N] slides** ✅ (verified with pdfinfo)
   - Ready for LinkedIn upload!

### Phase 6: Final Confirmation

**Wrap up and next steps:**

1. **Summary:**
   - Show created files (markdown + PDF)
   - Display file paths and sizes
   - Confirm successful generation
   - Report format (Square/Portrait) and file size

2. **LinkedIn upload tips:**
   - Upload PDF to LinkedIn as a document post
   - **Format specifications met:**
     * Square: 1080x1080px (1:1) ✓
     * Portrait: 1080x1350px (4:5) ✓
     * DPI: 300 (professional quality) ✓
     * Max file size: 100MB ✓
   - **Best practices:**
     * Recommended length: 8-12 slides for engagement
     * Write engaging caption for your post
     * Use 3-5 relevant hashtags
     * Post during peak engagement hours
     * Mobile-optimized design with large fonts
   - **Upload process:**
     * Click "Start a post" on LinkedIn
     * Click document icon
     * Upload your PDF
     * Add engaging caption
     * Post or schedule

3. **Offer improvements:**
   - "Would you like to make any changes to the carousel?"
   - "Need to adjust design, content, or backgrounds?"
   - "Want to create another carousel?"
   - "Should I help you write a LinkedIn caption for this carousel?"

## Marp Syntax Quick Reference

### Frontmatter Directives

```yaml
---
marp: true              # Enable Marp
theme: default          # Theme: default, gaia, uncover
paginate: true          # Show page numbers
backgroundColor: #fff   # Slide background color
color: #333             # Text color
class: lead             # Slide class (styling)
---
```

### Slide Separators

```markdown
---
```

### Background Images

```markdown
<!-- Full background -->
![bg](image.jpg)

<!-- Fit to slide -->
![bg fit](image.jpg)

<!-- Split backgrounds -->
![bg left](image1.jpg)
![bg right](image2.jpg)

<!-- Vertical split -->
![bg top](image1.jpg)
![bg bottom](image2.jpg)

<!-- With opacity -->
![bg opacity:.5](image.jpg)

<!-- Multiple backgrounds -->
![bg](image1.jpg)
![bg](image2.jpg)
![bg](image3.jpg)
```

### Local Directives (Per Slide)

```markdown
<!-- _class: lead -->
<!-- _backgroundColor: aqua -->
<!-- _color: white -->
<!-- _paginate: false -->
```

### Text Formatting

```markdown
# Heading 1 (Title)
## Heading 2 (Section)
### Heading 3 (Subsection)

**Bold text**
*Italic text*
`Code`

- Bullet point
1. Numbered list

> Quote or callout

[Link](url)
```

## LinkedIn Carousel Best Practices

### Content Strategy

1. **Hook on Slide 1:**
   - Attention-grabbing title
   - Clear value proposition
   - Visual interest

2. **Content Slides (2-N-1):**
   - One idea per slide
   - Use visuals when possible
   - Keep text minimal
   - Maintain consistency

3. **CTA on Final Slide:**
   - Clear call to action
   - Contact information
   - Follow request
   - Link to resource

### Design Guidelines

**Text:**
- Large, readable fonts
- High contrast
- 3-5 lines max per slide
- Consistent formatting

**Visuals:**
- High-quality images
- Relevant to content
- Consistent style
- Proper attribution

**Branding:**
- Include logo/watermark
- Consistent color scheme
- Professional appearance
- Contact info on last slide

### Optimal Carousel Length

- **5-7 slides**: Quick tips, announcements
- **8-10 slides**: Tutorials, guides, stories
- **11-15 slides**: In-depth content, case studies

**LinkedIn recommendation:** Keep it under 10 slides for best engagement

## Examples

### Example 1: Simple Text Carousel (5 Slides)

**User input:** "Create a carousel about 5 Python tips for beginners"

**Generated Marp:**
```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #fff
---

<!-- Slide 1: Title -->
# 5 Python Tips for Beginners 🐍

Master these fundamentals to level up your Python skills

---

<!-- Slide 2: Tip 1 -->
## 1. Use List Comprehensions

Replace verbose loops with elegant one-liners:

```python
# Instead of this:
squares = []
for x in range(10):
    squares.append(x**2)

# Do this:
squares = [x**2 for x in range(10)]
```

---

<!-- Slide 3: Tip 2 -->
## 2. F-Strings for Formatting

Modern, readable string formatting:

```python
name = "Alice"
age = 30

# Instead of: "Hello " + name
# Do this:
print(f"Hello {name}, you are {age}")
```

---

<!-- Slide 4: Tip 3 -->
## 3. Use enumerate()

Get index and value simultaneously:

```python
for index, value in enumerate(['a', 'b', 'c']):
    print(f"{index}: {value}")
```

---

<!-- Slide 5: CTA -->
# Want More Python Tips?

Follow me for weekly Python tutorials

Connect: @yourname
Web: yourwebsite.com

#Python #Programming #Coding

---
```

**Generated command:**
```bash
marp carousel-2025-10-23-python-tips.md -o carousel-2025-10-23-python-tips.pdf
```

### Example 2: Carousel with Background Images

**User input:** "Create a carousel about my product launch with branded backgrounds"

**Generated Marp:**
```markdown
---
marp: true
theme: gaia
paginate: true
---

<!-- Slide 1: Title with brand background -->
![bg](backgrounds/brand-hero.jpg)

# Introducing ProductX 🚀

The future of productivity is here

---

<!-- Slide 2: Problem -->
![bg opacity:.3](backgrounds/problem.jpg)

## The Problem

⏰ Teams waste 3 hours daily on inefficient workflows
📊 Communication gaps cost businesses $37B annually
🔄 Context switching reduces productivity by 40%

---

<!-- Slide 3: Solution -->
![bg left](backgrounds/solution.jpg)

## Our Solution

**ProductX** streamlines your workflow with:
- Unified communication
- Smart automation
- Real-time collaboration

---

<!-- Slide 4: Features -->
## Key Features

✅ **AI-Powered Insights**
✅ **Seamless Integrations**
✅ **Enterprise Security**
✅ **24/7 Support**

---

<!-- Slide 5: CTA -->
![bg](backgrounds/cta.jpg)

# Try ProductX Today

🎁 Free 30-day trial
🚀 No credit card required

Visit: productx.com

---
```

### Example 3: Educational Carousel (8 Slides)

**User input:** "Create a carousel explaining microservices architecture"

**Generated Marp:**
```markdown
---
marp: true
theme: uncover
paginate: true
---

<!-- Slide 1 -->
# Microservices Architecture 101

A beginner's guide to distributed systems

---

<!-- Slide 2 -->
## What are Microservices?

**Definition:**
Small, independent services that work together

Each service:
- Focuses on one business capability
- Runs in its own process
- Communicates via APIs

---

<!-- Slide 3 -->
## Monolith vs Microservices

**Monolith:** One large application
**Microservices:** Multiple small services

Key difference:
Independent deployment & scaling

---

<!-- Slide 4 -->
## Benefits

✅ **Scalability** - Scale services independently
✅ **Flexibility** - Use different technologies
✅ **Resilience** - Isolated failures
✅ **Speed** - Faster deployments

---

<!-- Slide 5 -->
## Challenges

⚠️ **Complexity** - More moving parts
⚠️ **Testing** - End-to-end testing harder
⚠️ **Monitoring** - Distributed debugging
⚠️ **Data** - Managing distributed data

---

<!-- Slide 6 -->
## When to Use Microservices?

**Good fit:**
- Large, complex applications
- Multiple teams
- Need for independent scaling
- Long-term projects

---

<!-- Slide 7 -->
## When NOT to Use?

**Not recommended:**
- Small applications
- Early-stage startups
- Limited resources
- Simple requirements

Start with monolith, evolve to microservices

---

<!-- Slide 8 -->
# Ready to Learn More?

Follow for more architecture insights

📧 Email: yourname@domain.com
🔗 LinkedIn: @yourname

#Microservices #Architecture #DevOps

---
```

## Error Handling

### Marp Installation Check

```bash
# Check if Marp CLI is installed
if ! command -v marp &> /dev/null; then
    echo "Marp CLI not found. Using npx..."
    npx @marp-team/marp-cli --version
fi
```

### Common Issues

**Marp not found:**
- Suggest: `npm install -g @marp-team/marp-cli`
- Or use: `npx @marp-team/marp-cli`

**Background image not found:**
- Verify absolute path
- Check file exists: `ls -lh /path/to/image`
- Suggest using `--allow-local-files` flag

**PDF generation fails:**
- Check Chrome/Chromium is installed (required by Marp)
- Try with `--pdf-notes` for debugging
- Verify write permissions in output directory

**Theme not applied:**
- Verify theme name (default, gaia, uncover)
- Check frontmatter syntax
- Ensure `marp: true` is set

## Quick Reference: Command Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `-o, --output` | Output file path | `marp input.md -o output.pdf` |
| `--theme` | Specify theme | `marp input.md --theme gaia` |
| `--pdf` | Force PDF output | `marp input.md --pdf` |
| `--allow-local-files` | Enable local images | `marp input.md --allow-local-files` |
| `--html` | Generate HTML | `marp input.md --html` |
| `--watch` | Watch mode | `marp input.md --watch` |
| `--preview` | Preview mode | `marp input.md --preview` |

## File Naming Convention

**Markdown source:**
```
carousel-YYYY-MM-DD-brief-topic.md
```

**PDF output:**
```
carousel-YYYY-MM-DD-brief-topic.pdf
```

**Examples:**
```
carousel-2025-10-23-python-tips.md
carousel-2025-10-23-python-tips.pdf

carousel-2025-10-25-product-launch.md
carousel-2025-10-25-product-launch.pdf
```

## Directory Structure

Suggest organizing files:

```
~/carousels/
├── 2025-10/
│   ├── carousel-2025-10-23-python-tips.md
│   ├── carousel-2025-10-23-python-tips.pdf
│   ├── carousel-2025-10-25-product-launch.md
│   └── carousel-2025-10-25-product-launch.pdf
└── backgrounds/
    ├── brand-hero.jpg
    ├── tech-bg.jpg
    └── gradient.jpg
```

## User Interaction Pattern

### Initial Engagement

**User:** "I want to create a LinkedIn carousel"

**Skill:** "I'll help you create a professional LinkedIn carousel using Marp! Let's start:

1. What content or topic would you like to include in your carousel?"

**User:** [Provides content]

**Skill:** "Great! Now:

2. How many slides would you like?
   - Recommended: 5-10 slides for LinkedIn
   - Slide 1: Hook/Title
   - Slides 2-N-1: Main content
   - Slide N: Call to action"

**User:** [Specifies number, e.g., "7 slides"]

**Skill:** "Perfect! Let me optimize your content for 7 slides. Here's the proposed structure:

[Shows slide breakdown]

Does this structure work for you, or would you like any adjustments?"

**User:** [Confirms or requests changes]

**Skill:** "Excellent! Now for the visual design:

3. Which theme would you like?
   - **default**: Clean, professional, minimal
   - **gaia**: Modern, colorful, bold
   - **uncover**: Minimalist, elegant, centered

What's your preference?"

**User:** [Chooses theme]

**Skill:** "Great choice! One more thing:

4. Would you like to add background images?
   - **No backgrounds**: Clean, text-only design
   - **Single background**: One image for all slides
   - **Per-slide backgrounds**: Different image for each slide"

**User:** [Specifies background preference]

**Skill:** [If backgrounds requested]
"Please provide the image file path(s) for the background(s)."

**User:** [Provides paths]

**Skill:** "Perfect! Creating your Marp carousel now...

[Generates markdown file]

Here's your Marp file:
[Shows content]

Generating PDF...

[Runs marp command]

✅ Carousel created successfully!

**Files:**
- Markdown: ~/carousels/carousel-2025-10-23-topic.md
- PDF: ~/carousels/carousel-2025-10-23-topic.pdf
- Size: [file size]

Your carousel is ready to upload to LinkedIn!

**LinkedIn Upload Tips:**
- Upload the PDF as a document
- Add an engaging caption
- Use relevant hashtags
- Optimal engagement: 5-10 slides

Would you like to make any changes or create another carousel?"

## Optimization Tips

### Content Optimization

**For LinkedIn carousels:**
- First slide: Stop-the-scroll hook
- Keep text minimal (3-5 bullet points max)
- One core idea per slide
- Use visual hierarchy
- End with clear CTA

**Text Guidelines:**
- Font size: Large and readable
- Contrast: High (dark text on light, or vice versa)
- Alignment: Consistent throughout
- Spacing: Generous white space

### Image Guidelines

**Background images:**
- High resolution (at least 1920x1080)
- Relevant to content
- Not too busy (text must be readable)
- Consider opacity for text overlay

**Best practices:**
- Use solid colors for text-heavy slides
- Use images for visual impact slides
- Maintain consistent style
- Compress images for smaller PDF size

## Advanced Features

### Custom Styling

```markdown
<!-- Scoped style for single slide -->
<style scoped>
h1 {
  color: #4A90E2;
  font-size: 3em;
}
</style>
```

### Two-Column Layouts

```markdown
<div style="display: flex;">
<div style="flex: 1;">

## Left Column
Content here

</div>
<div style="flex: 1;">

## Right Column
Content here

</div>
</div>
```

### Custom Classes

```markdown
<!-- _class: lead -->
# This slide uses the lead class

<!-- _class: invert -->
# This slide is inverted
```

## Troubleshooting

### PDF Quality Issues

```bash
# High quality PDF
marp input.md --pdf-outlines --allow-local-files -o output.pdf
```

### Font Issues

```markdown
---
marp: true
style: |
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
  section { font-family: 'Roboto', sans-serif; }
---
```

### Debugging

```bash
# Enable verbose output
marp input.md -o output.pdf --verbose

# Preview in browser before PDF
marp input.md --preview
```

## Complete Interaction Example

Here's a full example showing all phases of the carousel creation workflow:

**User:** "I want to create a LinkedIn carousel about Python tips for beginners"

**Skill:** "I'll help you create a professional LinkedIn carousel using Marp! Let's start:

1. What content would you like to include in your carousel? What are the main Python tips you want to share?"

**User:** "5 tips: list comprehensions, f-strings, enumerate, context managers, and type hints"

**Skill:** "Great content! Now:

2. How many slides would you like for this carousel?
   - Recommended: 5-10 slides for LinkedIn
   - Slide 1: Hook/Title
   - Slides 2-N-1: Main content (your tips)
   - Slide N: Call to action"

**User:** "7 slides total"

**Skill:** "Perfect! Here's the proposed structure:

```
Slide 1: 5 Python Tips for Beginners (Title/Hook)
Slide 2: Tip 1 - List Comprehensions
Slide 3: Tip 2 - F-Strings
Slide 4: Tip 3 - Enumerate
Slide 5: Tip 4 - Context Managers
Slide 6: Tip 5 - Type Hints
Slide 7: Follow for More Python Tips (CTA)
```

Does this structure work for you?"

**User:** "Yes, but I want Slide 3 to be just an image showing code examples"

**Skill:** "Excellent idea! I'll make Slide 3 an image-only slide. Now:

3. Which format would you like for your carousel?
   - **Square (1080x1080)**: Most versatile, works everywhere, 1:1 aspect ratio
   - **Portrait (1080x1350)**: More vertical space, mobile-optimized, 4:5 aspect ratio"

**User:** "Square format"

**Skill:** "Great choice! Now for the visual design:

4. Which Marp theme would you like?
   - **default**: Clean, professional, minimal
   - **gaia**: Modern, colorful, bold
   - **uncover**: Minimalist, elegant, centered"

**User:** "Gaia theme"

**Skill:** "Excellent! One more thing:

5. Would you like to add backgrounds to your slides?
   - **No backgrounds**: Text-only, clean design, minimal file size
   - **Solid color**: Single color background using CSS (lightweight)
   - **Single image**: One image for all slides
   - **Per-slide images**: Different image for each slide (can skip slides)"

**User:** "Solid color - a nice blue gradient"

**Skill:** "Perfect! What color or gradient would you like?
   Examples: `#4A90E2`, `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`"

**User:** "Use `linear-gradient(135deg, #4A90E2 0%, #2C5282 100%)`"

**Skill:** "Beautiful choice! Creating your carousel now...

[Generates Marp markdown file with all specifications]

Here's your carousel structure:
- Format: Square (1080x1080px)
- Theme: Gaia
- Background: Blue gradient
- Slides: 7 total (including 1 image-only slide)

Generating PDF...

[Runs marp command]

✅ Carousel created successfully!

**Files:**
- Markdown: ~/carousels/carousel-2025-10-23-python-tips.md
- PDF: ~/carousels/carousel-2025-10-23-python-tips.pdf
- Size: 245 KB
- Format: Square (1080x1080)
- Page count: 7 slides

**LinkedIn specifications met:**
✓ Dimensions: 1080x1080px (1:1)
✓ DPI: 300 (professional quality)
✓ File size: 245 KB (well under 100MB limit)
✓ Format: PDF/A compatible

Your carousel is ready to upload to LinkedIn!

**Upload tips:**
- Click 'Start a post' → Document icon → Upload PDF
- Add an engaging caption
- Use hashtags: #Python #Programming #Coding
- Post during peak hours for maximum engagement

Would you like to make any changes, or should I help you write a LinkedIn caption for this carousel?"

**User:** "Looks perfect! Yes, help me write a caption"

**Skill:** "Great! Here's a suggested caption for your Python carousel:

---
🐍 5 Python Tips Every Beginner Should Know

After teaching Python for 3+ years, these are the patterns that separate beginners from confident coders.

Swipe through for practical tips you can use TODAY →

What's your favorite Python feature? Drop it in the comments! 👇

#Python #Programming #Coding #LearnToCode #PythonTips

---

Would you like me to adjust the caption?"

## Resources

**Marp Documentation:**
- Official site: https://marp.app/
- Marpit framework: https://marpit.marp.app/
- GitHub: https://github.com/marp-team/marp-cli

**LinkedIn Carousel Specifications:**
- **Dimensions:**
  * Square: 1080x1080px (1:1 aspect ratio)
  * Portrait: 1080x1350px (4:5 aspect ratio)
- **File format:** PDF (PDF/A, PDF 1.4+, or PDF/X)
- **DPI:** 300 (professional quality, minimum 72)
- **File size:** Maximum 100MB
- **Page count:** Maximum 300 (recommended 8-12 for engagement)
- **Design:** Professional, consistent, mobile-optimized

## Important Notes

1. **Marp CLI Required**: Ensure Marp CLI is installed (`npm install -g @marp-team/marp-cli`) or use npx
2. **Format Selection**: Always ask user for Square (1080x1080) vs Portrait (1080x1350) format
3. **Image Paths**: Use absolute paths for background images and VALIDATE files exist
4. **Image-Only Slides**: Ask if user wants any slides to be image-only (no text)
5. **Background Options**: Support no backgrounds, solid colors (CSS), single image, or per-slide images
6. **Skip Slides**: When using per-slide backgrounds, allow user to skip specific slides
7. **Solid Colors**: Use CSS in frontmatter for lightweight PDFs
8. **Chromium/Chrome**: Required by Marp for PDF generation
9. **File Permissions**: Verify write access to output directory
10. **LinkedIn Format**: Upload as PDF document for best results
11. **Preview First**: Always preview before finalizing
12. **Optimization**: Keep file size under 100MB for LinkedIn upload
13. **Mobile-First**: Ensure large fonts and high contrast for mobile viewing
14. **⚠️ No Trailing Separator**: Never add `---` after the last slide (creates unwanted empty page)

## Final Checklist

Before completing the carousel:

✅ Content optimized for slide count (8-12 recommended)
✅ Proper slide structure (hook → content → CTA)
✅ Format selected (Square 1080x1080 or Portrait 1080x1350)
✅ Theme selected and applied (default/gaia/uncover)
✅ Background configuration complete:
   - If solid color: CSS gradient/color applied
   - If images: All paths validated and accessible
   - If per-slide: Skip slides properly handled
   - If image-only slides: Configured with `![bg cover]`
✅ Image-only slides (if requested) configured correctly
✅ Marp markdown syntax correct
✅ No trailing `---` after last slide (prevents empty page)
✅ PDF generated successfully with LinkedIn specs:
   - Dimensions correct (1080x1080 or 1080x1350)
   - DPI 300 (professional quality)
   - File size under 100MB
   - PDF/A compatible format
✅ File size verified with `ls -lh output.pdf`
✅ **Page count verified** - Check with:
   ```bash
   pdfinfo output.pdf | grep Pages
   # OR
   pdftk output.pdf dump_data | grep NumberOfPages
   ```
   Expected: N pages (matches requested slide count)
   Common issue: N+1 pages = trailing `---` in markdown
✅ Preview looks good (optional preview before finalizing)
✅ Mobile-optimized (large fonts, high contrast)
✅ Ready for LinkedIn upload!
