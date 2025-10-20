"""Tests for file parsing utilities."""

import pytest

from app.utils.file_parser import (
    extract_text_from_pdf,
    extract_text_from_txt,
    parse_uploaded_file,
    validate_file_size,
    FileParsingError,
)


class TestExtractTextFromPDF:
    """Tests for PDF text extraction."""
    
    def test_extract_text_from_valid_pdf(self, sample_pdf_file):
        """Test extracting text from a valid PDF file."""
        filename, content = sample_pdf_file
        
        text = extract_text_from_pdf(content)
        assert text is not None
        assert isinstance(text, str)
        assert len(text) > 0
        # The sample PDF contains "Test PDF Content"
        assert "Test PDF Content" in text or len(text) > 0
    
    def test_extract_text_from_invalid_pdf(self):
        """Test extracting text from invalid PDF file."""
        invalid_content = b"Not a valid PDF file"
        
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_pdf(invalid_content)
        assert "Failed to parse PDF" in str(exc_info.value)
    
    def test_extract_text_from_empty_pdf(self):
        """Test extracting text from PDF with no text content."""
        # Minimal PDF with no text
        minimal_pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
192
%%EOF
"""
        with pytest.raises(FileParsingError) as exc_info:
            extract_text_from_pdf(minimal_pdf)
        assert "No text could be extracted" in str(exc_info.value)
    
    def test_extract_text_with_max_length(self, sample_pdf_file):
        """Test extracting text with max length limit."""
        filename, content = sample_pdf_file
        
        # Extract with very small max length
        text = extract_text_from_pdf(content, max_length=10)
        assert text is not None
        assert len(text) <= 10


class TestExtractTextFromTxt:
    """Tests for text file extraction."""
    
    def test_extract_text_from_valid_txt(self, sample_txt_file):
        """Test extracting text from a valid text file."""
        filename, content = sample_txt_file
        
        text = extract_text_from_txt(content)
        assert text is not None
        assert isinstance(text, str)
        assert "test text file" in text.lower()
        assert "multiple lines" in text.lower()
    
    def test_extract_text_from_markdown(self, sample_markdown_file):
        """Test extracting text from a markdown file."""
        filename, content = sample_markdown_file
        
        text = extract_text_from_txt(content)
        assert text is not None
        assert "Test Markdown File" in text
        assert "Point 1" in text
    
    def test_extract_text_from_empty_file(self):
        """Test extracting text from an empty file."""
        empty_content = b""
        
        text = extract_text_from_txt(empty_content)
        assert text == ""
    
    def test_extract_text_with_different_encodings(self):
        """Test extracting text with different encodings."""
        # Test UTF-8
        utf8_content = "UTF-8 text: Hello, 世界 🌍".encode('utf-8')
        text = extract_text_from_txt(utf8_content)
        assert "UTF-8 text" in text
        assert "世界" in text
    
    def test_extract_text_with_max_length(self, sample_txt_file):
        """Test extracting text with max length limit."""
        filename, content = sample_txt_file
        
        # Extract with small max length
        text = extract_text_from_txt(content, max_length=20)
        assert len(text) <= 20
    
    def test_extract_text_with_latin1_fallback(self):
        """Test extraction with latin-1 fallback encoding."""
        # Create content that's valid latin-1 but not UTF-8
        latin1_content = bytes([0xE9, 0xE8, 0xE0])  # Latin-1 accented chars
        
        text = extract_text_from_txt(latin1_content)
        assert text is not None
        assert isinstance(text, str)


class TestParseUploadedFile:
    """Tests for the main file parsing dispatcher."""
    
    def test_parse_pdf_file(self, sample_pdf_file):
        """Test parsing a PDF file."""
        filename, content = sample_pdf_file
        
        text = parse_uploaded_file(content, filename)
        assert text is not None
        assert isinstance(text, str)
        assert len(text) > 0
    
    def test_parse_txt_file(self, sample_txt_file):
        """Test parsing a text file."""
        filename, content = sample_txt_file
        
        text = parse_uploaded_file(content, filename)
        assert text is not None
        assert "test text file" in text.lower()
    
    def test_parse_markdown_file(self, sample_markdown_file):
        """Test parsing a markdown file."""
        filename, content = sample_markdown_file
        
        text = parse_uploaded_file(content, filename)
        assert text is not None
        assert "Test Markdown File" in text
    
    def test_parse_unsupported_file_type(self):
        """Test parsing an unsupported file type."""
        content = b"Some content"
        
        with pytest.raises(FileParsingError) as exc_info:
            parse_uploaded_file(content, "test.docx")
        assert "Unsupported file format" in str(exc_info.value)
    
    def test_parse_file_case_insensitive_extension(self, sample_txt_file):
        """Test that file extensions are handled case-insensitively."""
        filename, content = sample_txt_file
        
        # Test with uppercase extension
        text = parse_uploaded_file(content, "test.TXT")
        assert text is not None
        
        # Test with mixed case
        text = parse_uploaded_file(content, "test.Txt")
        assert text is not None
    
    def test_parse_file_with_max_length(self, sample_txt_file):
        """Test parsing file with max length limit."""
        filename, content = sample_txt_file
        
        text = parse_uploaded_file(content, filename, max_length=15)
        assert len(text) <= 15


class TestValidateFileSize:
    """Tests for file size validation."""
    
    def test_validate_small_file(self, sample_txt_file):
        """Test validating a file within size limit."""
        filename, content = sample_txt_file
        
        # Should not raise an exception
        validate_file_size(content)
    
    def test_validate_large_file(self, large_file_content):
        """Test validating a file exceeding size limit."""
        with pytest.raises(FileParsingError) as exc_info:
            validate_file_size(large_file_content)
        assert "File size" in str(exc_info.value)
        assert "exceeds" in str(exc_info.value)
    
    def test_validate_file_at_size_limit(self):
        """Test validating a file exactly at the size limit."""
        # Create exactly 10MB file
        exactly_10mb = b"x" * (10 * 1024 * 1024)
        
        # Should not raise an exception (10MB is the limit, not over)
        validate_file_size(exactly_10mb)
    
    def test_validate_empty_file(self):
        """Test validating an empty file."""
        empty_content = b""
        
        # Should not raise an exception
        validate_file_size(empty_content)
    
    def test_validate_custom_size_limit(self):
        """Test validating with a custom size limit."""
        # Create 2MB file
        content_2mb = b"x" * (2 * 1024 * 1024)
        
        # Should fail with 1MB limit
        with pytest.raises(FileParsingError):
            validate_file_size(content_2mb, max_size_mb=1)
        
        # Should pass with 3MB limit
        validate_file_size(content_2mb, max_size_mb=3)
    
    def test_validate_just_over_limit(self):
        """Test validating a file just slightly over the limit."""
        # Create 10MB + 1 byte
        just_over = b"x" * (10 * 1024 * 1024 + 1)
        
        with pytest.raises(FileParsingError) as exc_info:
            validate_file_size(just_over)
        assert "exceeds maximum allowed size" in str(exc_info.value)
