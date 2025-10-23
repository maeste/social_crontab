# Marp Carousel Reference Guide

## Complete Marp Syntax

### Frontmatter Configuration

```yaml
---
marp: true                    # Enable Marp
theme: default               # Theme: default, gaia, uncover
paginate: true               # Show page numbers
header: 'Header text'        # Header on all slides
footer: 'Footer text'        # Footer on all slides
backgroundColor: #fff        # Background color
backgroundImage: url(img.jpg) # Global background image
color: #333                  # Text color
class: lead                  # Default slide class
size: 16:9                   # Aspect ratio (16:9, 4:3)
style: |                     # Inline CSS
  section {
    font-family: Arial;
  }
---
```

### Slide Directives

**Global Directives** (in frontmatter):
- Apply to all slides
- Set defaults

**Local Directives** (per slide):
- Override global settings
- Prefix with underscore: `_`

```markdown
<!-- _paginate: false -->
<!-- _header: '' -->
<!-- _footer: '' -->
<!-- _backgroundColor: aqua -->
<!-- _color: white -->
<!-- _class: lead -->
```

### Background Image Syntax

**Basic background:**
```markdown
![bg](image.jpg)
```

**Size keywords:**
```markdown
![bg fit](image.jpg)      # Fit to slide
![bg contain](image.jpg)  # Contain within slide
![bg cover](image.jpg)    # Cover entire slide (default)
![bg auto](image.jpg)     # Original size
![bg 200%](image.jpg)     # Custom size percentage
```

**Position keywords:**
```markdown
![bg left](image.jpg)     # Left half
![bg right](image.jpg)    # Right half
![bg top](image.jpg)      # Top half
![bg bottom](image.jpg)   # Bottom half
```

**Filters:**
```markdown
![bg blur](image.jpg)             # Blur effect
![bg brightness:.5](image.jpg)    # Brightness (0-1+)
![bg contrast:1.5](image.jpg)     # Contrast adjustment
![bg grayscale](image.jpg)        # Grayscale filter
![bg hue-rotate:180deg](image.jpg) # Hue rotation
![bg invert](image.jpg)           # Invert colors
![bg opacity:.3](image.jpg)       # Transparency (0-1)
![bg saturate:2.0](image.jpg)     # Saturation
![bg sepia](image.jpg)            # Sepia tone
```

**Multiple filters:**
```markdown
![bg opacity:.5 blur:5px](image.jpg)
![bg brightness:.7 contrast:1.2](image.jpg)
```

**Multiple backgrounds:**
```markdown
<!-- Split backgrounds -->
![bg left](image1.jpg)
![bg right](image2.jpg)

<!-- Vertical split -->
![bg top](image1.jpg)
![bg bottom](image2.jpg)

<!-- 50/50 split with custom sizes -->
![bg left:50%](image1.jpg)
![bg right:50%](image2.jpg)

<!-- Multiple layers -->
![bg](layer1.jpg)
![bg opacity:.5](layer2.jpg)
![bg opacity:.3](layer3.jpg)
```

### Theme Classes

**Default theme classes:**
```markdown
<!-- _class: lead -->
# Centered, large text slide

<!-- _class: invert -->
# Inverted colors

<!-- _class: gaia -->
# Gaia theme styling
```

### Custom Styling

**Inline styles:**
```markdown
<style scoped>
section {
  background: linear-gradient(to bottom, #67b26f, #4ca2cd);
  color: white;
}
h1 {
  font-size: 3em;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}
</style>
```

**Global styles:**
```markdown
---
marp: true
style: |
  section {
    font-family: 'Arial', sans-serif;
  }
  h1 {
    color: #4A90E2;
  }
---
```

### HTML in Markdown

```markdown
<div style="display: flex; justify-content: space-between;">
  <div style="flex: 1;">Left content</div>
  <div style="flex: 1;">Right content</div>
</div>

<span style="color: red;">Red text</span>

<img src="logo.png" style="width: 100px; float: right;">
```

## LinkedIn Carousel Design Patterns

### Pattern 1: Tutorial/How-To

```markdown
Slide 1: "How to [Achieve Result]"
Slide 2: "Why this matters"
Slide 3-N-1: Step-by-step instructions
Slide N: "Results + CTA"
```

**Example structure:**
```
1. How to Build Microservices (title)
2. Why microservices matter (context)
3. Step 1: Define service boundaries
4. Step 2: Choose communication patterns
5. Step 3: Implement API gateway
6. Step 4: Set up monitoring
7. Results you'll achieve + Follow for more
```

### Pattern 2: Listicle

```markdown
Slide 1: "X Things You Should Know About [Topic]"
Slide 2-N-1: One item per slide
Slide N: "Summary + CTA"
```

**Example structure:**
```
1. 7 Python Mistakes to Avoid
2. Mistake 1: Not using virtual environments
3. Mistake 2: Ignoring type hints
4. Mistake 3: Poor error handling
5. Mistake 4: Not writing tests
6. Mistake 5: Hardcoding values
7. Mistake 6: Inefficient loops
8. Mistake 7: Not documenting code
9. Avoid these mistakes + Connect with me
```

### Pattern 3: Before/After

```markdown
Slide 1: "Transform Your [X]"
Slide 2: "The problem (before)"
Slide 3-N-1: The solution (steps/features)
Slide N: "The result (after) + CTA"
```

**Example structure:**
```
1. Transform Your Development Workflow
2. Before: Chaotic deployments, frequent bugs
3. Solution 1: CI/CD pipeline
4. Solution 2: Automated testing
5. Solution 3: Code review process
6. After: Reliable releases, happy team
7. Want this transformation? Let's talk
```

### Pattern 4: Story/Case Study

```markdown
Slide 1: Hook (the problem/challenge)
Slide 2: Background/context
Slide 3-N-2: The journey/solution
Slide N-1: Results/lessons learned
Slide N: Takeaway + CTA
```

**Example structure:**
```
1. How I Scaled to 1M Users
2. Started with monolith, hit scaling limits
3. Decision: Microservices architecture
4. Challenge 1: Data consistency
5. Challenge 2: Service communication
6. Challenge 3: Monitoring complexity
7. Results: 10x performance, zero downtime
8. Key lessons + Follow for more stories
```

### Pattern 5: Comparison

```markdown
Slide 1: "[Option A] vs [Option B]"
Slide 2-3: Option A (pros/cons)
Slide 4-5: Option B (pros/cons)
Slide 6: When to use each
Slide 7: Recommendation + CTA
```

**Example structure:**
```
1. REST vs GraphQL: Which to Choose?
2. REST: Simple, widely adopted, cacheable
3. REST: But... over-fetching, multiple requests
4. GraphQL: Flexible, single endpoint, type-safe
5. GraphQL: But... complexity, caching challenges
6. Use REST when: Simple CRUD, public APIs
7. Use GraphQL when: Complex queries, mobile apps
8. My recommendation + Questions?
```

## Color Schemes for LinkedIn

### Professional Color Palettes

**Blue (Trust, Corporate):**
```yaml
Primary: #0077B5 (LinkedIn Blue)
Secondary: #00A0DC
Accent: #0A66C2
Background: #F3F6F8
Text: #000000
```

**Green (Growth, Tech):**
```yaml
Primary: #10B981
Secondary: #059669
Accent: #34D399
Background: #ECFDF5
Text: #065F46
```

**Purple (Creative, Innovation):**
```yaml
Primary: #8B5CF6
Secondary: #7C3AED
Accent: #A78BFA
Background: #F5F3FF
Text: #5B21B6
```

**Orange (Energy, Bold):**
```yaml
Primary: #F59E0B
Secondary: #D97706
Accent: #FBBF24
Background: #FFFBEB
Text: #92400E
```

**Gradient Backgrounds:**
```css
/* Cool professional */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Warm energetic */
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Nature/Growth */
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* Sunset */
background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
```

## Typography Best Practices

### Font Sizes

```markdown
---
style: |
  section {
    font-size: 28px;        # Body text
  }
  h1 { font-size: 72px; }   # Main title
  h2 { font-size: 48px; }   # Section headers
  h3 { font-size: 36px; }   # Subsections
  code { font-size: 24px; } # Code blocks
---
```

### Font Pairing

**Professional:**
```css
font-family: 'Helvetica Neue', Arial, sans-serif;
```

**Modern:**
```css
font-family: 'Roboto', 'Open Sans', sans-serif;
```

**Technical:**
```css
/* Headings */
font-family: 'Inter', 'SF Pro Display', sans-serif;
/* Code */
font-family: 'Fira Code', 'JetBrains Mono', monospace;
```

**Creative:**
```css
font-family: 'Montserrat', 'Poppins', sans-serif;
```

### Text Hierarchy

```markdown
# Title (Most Important)
## Section Header (Very Important)
### Subsection (Important)
Regular text (Supporting)
*Italics for emphasis*
**Bold for strong emphasis**
`Code for technical terms`
```

## Layout Patterns

### Centered Content

```markdown
<!-- _class: lead -->

# Main Title

Subtitle or supporting text

---
```

### Two-Column Layout

```markdown
<div class="columns">
<div>

## Left Column

- Point 1
- Point 2
- Point 3

</div>
<div>

## Right Column

- Point 4
- Point 5
- Point 6

</div>
</div>

<style scoped>
.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}
</style>
```

### Card Layout

```markdown
<div class="cards">
<div class="card">

### Feature 1
Description

</div>
<div class="card">

### Feature 2
Description

</div>
<div class="card">

### Feature 3
Description

</div>
</div>

<style scoped>
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
```

### Image + Text Layout

```markdown
![bg left:40%](image.jpg)

## Content Area

Text content appears on the right
when image is positioned left

---

![bg right:40%](image.jpg)

## Content Area

Text content appears on the left
when image is positioned right
```

## Icon and Emoji Usage

### Professional Emojis for LinkedIn

**Technology:**
💻 🖥️ ⌨️ 🖱️ 💾 📱 🔌 🔋 ⚡ 🔧 🛠️ ⚙️

**Business:**
📊 📈 📉 💼 💰 💳 🏢 🏦 📋 📝 📄 📌

**Communication:**
💬 📧 📞 📢 📣 🔔 ✉️ 💭 🗨️ 📮 📬

**Success/Achievement:**
🎯 🏆 ✅ ✔️ 👍 🎉 🚀 ⭐ 💡 🔥 💪

**Learning/Education:**
📚 📖 📕 📗 📘 📙 🎓 🧠 💭 📝 ✏️ 🖊️

**Development:**
🐍 (Python) ☕ (Java) 🦀 (Rust) 🐳 (Docker) ☸️ (Kubernetes)

### Icon Fonts

```markdown
---
style: |
  @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
---

<!-- Use Font Awesome icons -->
<i class="fas fa-check"></i> Completed
<i class="fas fa-times"></i> Failed
<i class="fas fa-rocket"></i> Launch
```

## Code Block Styling

### Syntax Highlighting

```markdown
\```python
def hello_world():
    print("Hello, LinkedIn!")
    return True
\```

\```javascript
const greeting = () => {
  console.log("Hello, LinkedIn!");
  return true;
};
\```

\```bash
# Install dependencies
npm install @marp-team/marp-cli
\```
```

### Custom Code Styling

```markdown
---
style: |
  pre {
    background: #1e1e1e;
    border-radius: 8px;
    padding: 1.5rem;
  }
  code {
    font-family: 'Fira Code', monospace;
    font-size: 18px;
    line-height: 1.5;
  }
---
```

## Call-to-Action Patterns

### Effective CTA Slides

**Connect CTA:**
```markdown
# Let's Connect! 🤝

📧 yourname@email.com
💼 linkedin.com/in/yourname
🐦 @yourname
🌐 yourwebsite.com

Follow for more [topic] insights
```

**Learn More CTA:**
```markdown
# Want to Learn More?

📚 Free guide: [Link to resource]
🎥 Watch my video series
📧 Join my newsletter
👉 Comment "GUIDE" for the download link
```

**Engagement CTA:**
```markdown
# Your Turn!

What's your experience with [topic]?

💬 Comment below
🔁 Share if helpful
👍 Save for later

Let's discuss in the comments! 👇
```

**Product/Service CTA:**
```markdown
# Ready to Get Started?

✨ Free trial available
📅 Book a demo
💬 Questions? DM me

Visit: yourproduct.com
```

## Marp CLI Advanced Usage

### Watch Mode

```bash
# Auto-rebuild on changes
marp input.md --watch

# With preview
marp input.md --watch --preview
```

### Multiple Files

```bash
# Convert all markdown files
marp *.md

# Specific directory
marp slides/*.md --output pdfs/
```

### Custom Theme

```bash
# Use custom theme CSS
marp input.md --theme custom-theme.css

# Theme directory
marp input.md --theme-set themes/
```

### Export Options

```bash
# Export as HTML
marp input.md --html -o output.html

# Export as PPTX
marp input.md --pptx -o output.pptx

# Multiple formats
marp input.md --pdf --html --pptx
```

### Configuration File

Create `marp.config.js`:

```javascript
module.exports = {
  inputDir: './slides',
  output: './output',
  pdf: true,
  allowLocalFiles: true,
  themeSet: './themes'
}
```

Run with config:
```bash
marp --config-file marp.config.js
```

## Optimization Tips

### File Size Reduction

**Compress images:**
```bash
# Before adding to Marp
convert input.jpg -quality 85 -resize 1920x1080 output.jpg
```

**Optimize PDF:**
```bash
# After Marp generation
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET \
   -dBATCH -sOutputFile=output-compressed.pdf input.pdf
```

### Performance

**Use local images:**
- Faster than remote URLs
- More reliable
- Better quality control

**Limit animations:**
- PDFs don't support animations well
- Focus on static design for LinkedIn

**Test on mobile:**
- LinkedIn mobile app is common
- Ensure text is readable
- Check tap targets

## LinkedIn Upload Checklist

✅ **File Format:**
- PDF (preferred)
- Image carousel (PNG/JPG alternative)

✅ **Dimensions:**
- Square: 1080x1080px
- Vertical: 1080x1350px
- Horizontal: 1200x628px

✅ **File Size:**
- Under 100MB (LinkedIn limit)
- Smaller = faster upload/viewing

✅ **Content:**
- First slide has strong hook
- Each slide has clear focus
- Last slide has clear CTA
- Text is readable on mobile

✅ **Branding:**
- Consistent colors
- Logo present
- Contact info included
- Professional appearance

✅ **Engagement:**
- Value-driven content
- Clear takeaways
- Question or CTA
- Relevant hashtags in caption

## Common Mistakes to Avoid

❌ **Too much text per slide**
✅ Keep it to 3-5 bullet points max

❌ **Low contrast (hard to read)**
✅ Use high contrast: dark on light or light on dark

❌ **Inconsistent styling**
✅ Maintain consistent fonts, colors, spacing

❌ **No clear flow**
✅ Logical progression from slide to slide

❌ **Missing CTA**
✅ Always end with clear next step

❌ **Unprofessional images**
✅ High-quality, relevant visuals only

❌ **Too many slides**
✅ Keep it under 10 for optimal engagement

❌ **Tiny fonts**
✅ Large, readable text (mobile-friendly)

## Testing Workflow

Before finalizing:

1. **Preview in Marp:**
   ```bash
   marp input.md --preview
   ```

2. **Generate PDF:**
   ```bash
   marp input.md -o output.pdf
   ```

3. **Check PDF:**
   - Open in PDF viewer
   - Verify all slides render correctly
   - Check text readability
   - Verify images load

4. **Mobile Test:**
   - View PDF on phone
   - Ensure text is readable
   - Check tap functionality

5. **LinkedIn Test:**
   - Upload to LinkedIn (as draft)
   - Preview carousel
   - Test navigation
   - Check appearance in feed

## Resources

**Marp Resources:**
- Official docs: https://marp.app/
- Themes: https://github.com/marp-team/marp-core/tree/main/themes
- Examples: https://github.com/marp-team/marp-cli/tree/main/examples

**Design Resources:**
- Unsplash: Free high-quality images
- Pexels: Free stock photos
- Canva: Design templates
- Coolors: Color palette generator

**LinkedIn Resources:**
- LinkedIn carousel guide
- Best practices for engagement
- Optimal posting times
- Hashtag research tools

## Quick Start Template

Save as `template-carousel.md`:

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #fff
---

<!-- Slide 1: Title/Hook -->
# [Your Attention-Grabbing Title]

[Subtitle or value proposition]

---

<!-- Slide 2: Problem/Context -->
## [Why This Matters]

- Point 1
- Point 2
- Point 3

---

<!-- Slide 3: Solution/Content -->
## [Your Main Point]

Key insight or information

---

<!-- Additional content slides... -->

---

<!-- Final Slide: CTA -->
# [Clear Call to Action]

📧 your@email.com
💼 LinkedIn: @yourname

#YourHashtags

---
```

Use this as starting point for any carousel!
