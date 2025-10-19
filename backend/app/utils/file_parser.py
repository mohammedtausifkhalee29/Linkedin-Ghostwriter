"""File parsing utilities for extracting text from various file formats."""

import io
from typing import Optional

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class FileParsingError(Exception):
    """Exception raised when file parsing fails."""
    pass


def extract_text_from_pdf(file_content: bytes, max_length: int = 10000) -> str:
    """
    Extract text from PDF file using PyMuPDF.
    
    Args:
        file_content: Binary content of the PDF file
        max_length: Maximum length of extracted text
        
    Returns:
        Extracted text from the PDF
        
    Raises:
        FileParsingError: If PDF parsing fails
    """
    if not PYMUPDF_AVAILABLE:
        raise FileParsingError("PyMuPDF is not installed. Please install it with: pip install pymupdf")
    
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        
        text_parts = []
        total_length = 0
        
        # Extract text from each page
        for page_num in range(pdf_document.page_count):
            if total_length >= max_length:
                break
                
            page = pdf_document[page_num]
            page_text = page.get_text()
            
            # Add page text
            remaining_length = max_length - total_length
            if len(page_text) > remaining_length:
                text_parts.append(page_text[:remaining_length])
                break
            else:
                text_parts.append(page_text)
                total_length += len(page_text)
        
        pdf_document.close()
        
        extracted_text = "\n".join(text_parts).strip()
        
        if not extracted_text:
            raise FileParsingError("No text could be extracted from the PDF")
        
        return extracted_text
        
    except Exception as e:
        raise FileParsingError(f"Failed to parse PDF: {str(e)}")


def extract_text_from_txt(file_content: bytes, max_length: int = 10000) -> str:
    """
    Extract text from plain text file.
    
    Args:
        file_content: Binary content of the text file
        max_length: Maximum length of extracted text
        
    Returns:
        Extracted text from the file
        
    Raises:
        FileParsingError: If text parsing fails
    """
    try:
        # Try UTF-8 first
        text = file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback to latin-1
            text = file_content.decode('latin-1')
        except Exception as e:
            raise FileParsingError(f"Failed to decode text file: {str(e)}")
    
    # Truncate if necessary
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def parse_uploaded_file(file_content: bytes, filename: str, max_length: int = 10000) -> str:
    """
    Parse uploaded file and extract text content.
    
    Args:
        file_content: Binary content of the file
        filename: Name of the uploaded file
        max_length: Maximum length of extracted text
        
    Returns:
        Extracted text from the file
        
    Raises:
        FileParsingError: If file parsing fails or format is unsupported
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content, max_length)
    elif filename_lower.endswith(('.txt', '.md')):
        return extract_text_from_txt(file_content, max_length)
    else:
        raise FileParsingError(
            f"Unsupported file format. Supported formats: PDF, TXT, MD. Got: {filename}"
        )


def validate_file_size(file_content: bytes, max_size_mb: float = 10.0) -> None:
    """
    Validate that file size is within acceptable limits.
    
    Args:
        file_content: Binary content of the file
        max_size_mb: Maximum allowed file size in megabytes
        
    Raises:
        FileParsingError: If file is too large
    """
    file_size_mb = len(file_content) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        raise FileParsingError(
            f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
        )
