"""Tests for post file parser."""

import pytest
from pathlib import Path
from datetime import datetime
from socialcli.utils.parser import PostParser


@pytest.fixture
def temp_post_file(tmp_path):
    """Create a temporary post file."""
    def _create_file(content: str, filename: str = "post.md"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)
    return _create_file


class TestPostParserBasic:
    """Test basic parser functionality."""

    def test_parse_simple_post_without_front_matter(self, temp_post_file):
        """Test parsing a simple post without front matter."""
        content = "This is a simple post without front matter."
        file_path = temp_post_file(content)

        parser = PostParser(file_path)

        assert parser.get_content() == content
        assert parser.get_title() is None
        assert parser.get_tags() == []
        assert parser.get_provider() is None
        assert parser.get_schedule() is None
        assert not parser.has_front_matter()

    def test_parse_post_with_front_matter(self, temp_post_file):
        """Test parsing a post with complete front matter."""
        content = """---
title: Test Post
tags: [AI, Tech]
provider: linkedin
schedule: 2025-10-21T09:00:00
---

This is the post content."""

        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_title() == "Test Post"
        assert parser.get_tags() == ['AI', 'Tech']
        assert parser.get_provider() == "linkedin"
        assert parser.get_schedule() == "2025-10-21T09:00:00"
        assert parser.get_content() == "This is the post content."
        assert parser.has_front_matter()

    def test_file_not_found_raises_error(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            PostParser("/nonexistent/file.md")


class TestFrontMatterParsing:
    """Test YAML front matter parsing."""

    def test_parse_title(self, temp_post_file):
        """Test parsing title from front matter."""
        content = """---
title: My Post Title
---

Content here."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_title() == "My Post Title"

    def test_parse_tags_as_list(self, temp_post_file):
        """Test parsing tags as YAML list."""
        content = """---
tags: [AI, Tech, Innovation]
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_tags() == ['AI', 'Tech', 'Innovation']

    def test_parse_tags_as_comma_separated_string(self, temp_post_file):
        """Test parsing tags as comma-separated string."""
        content = """---
tags: AI, Tech, Innovation
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_tags() == ['AI', 'Tech', 'Innovation']

    def test_parse_provider(self, temp_post_file):
        """Test parsing provider from front matter."""
        content = """---
provider: linkedin
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_provider() == "linkedin"

    def test_parse_schedule_iso_format(self, temp_post_file):
        """Test parsing schedule in ISO format."""
        content = """---
schedule: 2025-10-21T09:00:00
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_schedule() == "2025-10-21T09:00:00"

    def test_parse_schedule_datetime_object(self, temp_post_file):
        """Test parsing schedule as datetime object."""
        # YAML can parse datetime directly
        content = """---
schedule: 2025-10-21 09:00:00
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        schedule = parser.get_schedule()
        assert schedule is not None
        # Should be converted to ISO format string
        assert isinstance(schedule, str)

    def test_invalid_schedule_format_raises_error(self, temp_post_file):
        """Test that invalid schedule format raises ValueError."""
        content = """---
schedule: not-a-date
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        with pytest.raises(ValueError, match="Invalid schedule format"):
            parser.get_schedule()

    def test_invalid_yaml_raises_error(self, temp_post_file):
        """Test that invalid YAML raises ValueError."""
        content = """---
title: Test
invalid yaml here: [
---

Content."""
        file_path = temp_post_file(content)

        with pytest.raises(ValueError, match="Invalid YAML"):
            PostParser(file_path)

    def test_empty_front_matter(self, temp_post_file):
        """Test post with empty front matter section."""
        content = """---

---

Content here."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_content() == "Content here."
        assert not parser.has_front_matter()

    def test_custom_metadata_fields(self, temp_post_file):
        """Test accessing custom metadata fields."""
        content = """---
title: Test
author: John Doe
custom_field: custom_value
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_metadata_field('author') == 'John Doe'
        assert parser.get_metadata_field('custom_field') == 'custom_value'
        assert parser.get_metadata_field('nonexistent') is None
        assert parser.get_metadata_field('nonexistent', 'default') == 'default'


class TestContentExtraction:
    """Test content body extraction."""

    def test_extract_content_with_front_matter(self, temp_post_file):
        """Test extracting content when front matter is present."""
        content = """---
title: Test
---

Line 1
Line 2
Line 3"""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_content() == "Line 1\nLine 2\nLine 3"

    def test_extract_content_without_front_matter(self, temp_post_file):
        """Test extracting content when no front matter."""
        content = "Just plain content\nwith multiple lines"
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_content() == content

    def test_extract_multiline_content(self, temp_post_file):
        """Test extracting multiline content with markdown."""
        content = """---
title: Test
---

# Heading

This is **bold** text.

- List item 1
- List item 2

End of post."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        expected_content = """# Heading

This is **bold** text.

- List item 1
- List item 2

End of post."""
        assert parser.get_content() == expected_content

    def test_content_whitespace_stripped(self, temp_post_file):
        """Test that leading/trailing whitespace is stripped from content."""
        content = """---
title: Test
---


   Content with whitespace


"""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_content() == "Content with whitespace"


class TestValidation:
    """Test parser validation."""

    def test_validate_valid_post(self, temp_post_file):
        """Test validating a valid post."""
        content = """---
title: Test
schedule: 2025-10-21T09:00:00
---

Valid content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.validate() is True

    def test_validate_empty_content_raises_error(self, temp_post_file):
        """Test that empty content fails validation."""
        content = """---
title: Test
---

"""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        with pytest.raises(ValueError, match="content cannot be empty"):
            parser.validate()

    def test_validate_invalid_schedule_raises_error(self, temp_post_file):
        """Test that invalid schedule fails validation."""
        content = """---
schedule: invalid-date
---

Content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        with pytest.raises(ValueError, match="Invalid schedule format"):
            parser.validate()


class TestToDictMethod:
    """Test to_dict conversion."""

    def test_to_dict_with_all_fields(self, temp_post_file):
        """Test converting post with all fields to dict."""
        content = """---
title: Test Post
tags: [AI, Tech]
provider: linkedin
schedule: 2025-10-21T09:00:00
---

Post content."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        result = parser.to_dict()

        assert result['title'] == "Test Post"
        assert result['tags'] == ['AI', 'Tech']
        assert result['provider'] == "linkedin"
        assert result['schedule'] == "2025-10-21T09:00:00"
        assert result['content'] == "Post content."
        assert 'metadata' in result

    def test_to_dict_minimal_post(self, temp_post_file):
        """Test converting minimal post to dict."""
        content = "Just content."
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        result = parser.to_dict()

        assert result['title'] is None
        assert result['tags'] == []
        assert result['provider'] is None
        assert result['schedule'] is None
        assert result['content'] == "Just content."


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_post_with_dashes_in_content(self, temp_post_file):
        """Test that dashes in content don't confuse parser."""
        content = """---
title: Test
---

Content with --- dashes --- in it."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_content() == "Content with --- dashes --- in it."

    def test_post_with_yaml_like_content(self, temp_post_file):
        """Test post with YAML-like content in body."""
        content = """---
title: Test
---

key: value
another_key: another_value"""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert "key: value" in parser.get_content()
        assert parser.get_title() == "Test"

    def test_markdown_file_extension(self, temp_post_file):
        """Test parsing .md file."""
        content = "Markdown content"
        file_path = temp_post_file(content, "test.md")
        parser = PostParser(file_path)

        assert parser.get_content() == "Markdown content"

    def test_text_file_extension(self, temp_post_file):
        """Test parsing .txt file."""
        content = "Text content"
        file_path = temp_post_file(content, "test.txt")
        parser = PostParser(file_path)

        assert parser.get_content() == "Text content"

    def test_unicode_content(self, temp_post_file):
        """Test parsing content with unicode characters."""
        content = """---
title: Test 测试
---

Content with émojis 🎉 and spëcial çharacters."""
        file_path = temp_post_file(content)
        parser = PostParser(file_path)

        assert parser.get_title() == "Test 测试"
        assert "🎉" in parser.get_content()
        assert "spëcial" in parser.get_content()
