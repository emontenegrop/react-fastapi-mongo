"""Tests for file validation utilities"""

import pytest
from io import BytesIO
from fastapi import UploadFile

from app.utils.file_validation import (
    validate_file_size, validate_file_extension, sanitize_filename,
    validate_file, validate_content_type
)
from app.utils.exceptions import DetailHttpException


class TestFileValidation:
    """Test cases for file validation utilities"""
    
    def test_validate_file_extension_valid(self):
        """Test validation of valid file extensions"""
        valid_extensions = [
            "document.pdf", "file.docx", "image.jpg", 
            "archive.zip", "text.txt", "data.csv"
        ]
        
        for filename in valid_extensions:
            # Should not raise exception
            assert validate_file_extension(filename) == True
    
    def test_validate_file_extension_invalid(self):
        """Test validation of invalid file extensions"""
        invalid_extensions = [
            "virus.exe", "script.bat", "malware.vbs",
            "danger.js", "harmful.php", "bad.sh"
        ]
        
        for filename in invalid_extensions:
            with pytest.raises(DetailHttpException) as exc_info:
                validate_file_extension(filename)
            assert exc_info.value.status_code == 422
    
    def test_validate_file_extension_unsupported(self):
        """Test validation of unsupported file extensions"""
        unsupported_extensions = [
            "file.xyz", "document.unknown", "test.abc"
        ]
        
        for filename in unsupported_extensions:
            with pytest.raises(DetailHttpException) as exc_info:
                validate_file_extension(filename)
            assert exc_info.value.status_code == 422
    
    def test_validate_file_extension_empty_filename(self):
        """Test validation with empty filename"""
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file_extension("")
        assert exc_info.value.status_code == 422
    
    def test_validate_file_extension_none_filename(self):
        """Test validation with None filename"""
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file_extension(None)
        assert exc_info.value.status_code == 422
    
    def test_sanitize_filename_normal(self):
        """Test filename sanitization with normal names"""
        test_cases = [
            ("document.pdf", "document.pdf"),
            ("my file.txt", "my file.txt"),
            ("test_file.docx", "test_file.docx")
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
    
    def test_sanitize_filename_forbidden_chars(self):
        """Test filename sanitization with forbidden characters"""
        test_cases = [
            ("file<name>.pdf", "file_name_.pdf"),
            ("doc:ument.txt", "doc_ument.txt"),
            ("test|file.docx", "test_file.docx"),
            ("file\"name.pdf", "file_name.pdf"),
            ("path/file.txt", "file.txt")  # Path traversal prevention
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
    
    def test_sanitize_filename_reserved_names(self):
        """Test filename sanitization with Windows reserved names"""
        reserved_names = ["CON.txt", "PRN.pdf", "AUX.docx", "NUL.zip"]
        
        for reserved_name in reserved_names:
            result = sanitize_filename(reserved_name)
            assert result.startswith("file_")
            assert not result.upper().startswith(reserved_name.split('.')[0])
    
    def test_sanitize_filename_empty(self):
        """Test filename sanitization with empty string"""
        result = sanitize_filename("")
        assert result == "unnamed_file"
    
    def test_sanitize_filename_none(self):
        """Test filename sanitization with None"""
        result = sanitize_filename(None)
        assert result == "unnamed_file"
    
    def test_sanitize_filename_too_long(self):
        """Test filename sanitization with very long names"""
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid sizes"""
        # Create a small file (1KB)
        small_content = b"a" * 1024
        file = UploadFile(
            filename="small.txt",
            file=BytesIO(small_content),
            content_type="text/plain"
        )
        
        # Should not raise exception
        assert validate_file_size(file) == True
    
    def test_validate_file_size_too_large(self):
        """Test file size validation with oversized file"""
        # Create a file larger than the default limit (10MB)
        large_content = b"a" * (11 * 1024 * 1024)  # 11MB
        file = UploadFile(
            filename="large.txt", 
            file=BytesIO(large_content),
            content_type="text/plain"
        )
        
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file_size(file)
        assert exc_info.value.status_code == 413
    
    def test_validate_content_type_valid(self):
        """Test content type validation with valid types"""
        valid_types = [
            "application/pdf",
            "application/msword", 
            "text/plain",
            "image/jpeg",
            "application/zip"
        ]
        
        for content_type in valid_types:
            file = UploadFile(
                filename="test.file",
                file=BytesIO(b"content"),
                content_type=content_type
            )
            # Should not raise exception
            assert validate_content_type(file) == True
    
    def test_validate_content_type_invalid(self):
        """Test content type validation with invalid types"""
        invalid_types = [
            "application/x-executable",
            "text/x-shellscript",
            "application/x-dosexec"
        ]
        
        for content_type in invalid_types:
            file = UploadFile(
                filename="test.file",
                file=BytesIO(b"content"),
                content_type=content_type
            )
            with pytest.raises(DetailHttpException) as exc_info:
                validate_content_type(file)
            assert exc_info.value.status_code == 422
    
    def test_validate_file_complete_valid(self):
        """Test complete file validation with valid file"""
        content = b"test pdf content"
        file = UploadFile(
            filename="document.pdf",
            file=BytesIO(content),
            content_type="application/pdf"
        )
        
        result = validate_file(file)
        assert result == "document.pdf"
    
    def test_validate_file_no_file(self):
        """Test complete file validation with no file"""
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file(None)
        assert exc_info.value.status_code == 422
    
    def test_validate_file_no_filename(self):
        """Test complete file validation with no filename"""
        file = UploadFile(
            filename=None,
            file=BytesIO(b"content"),
            content_type="application/pdf"
        )
        
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file(file)
        assert exc_info.value.status_code == 422
    
    def test_validate_file_dangerous_extension(self):
        """Test complete file validation with dangerous extension"""
        file = UploadFile(
            filename="virus.exe",
            file=BytesIO(b"malicious content"),
            content_type="application/x-executable"
        )
        
        with pytest.raises(DetailHttpException) as exc_info:
            validate_file(file)
        assert exc_info.value.status_code == 422
    
    def test_validate_file_sanitizes_name(self):
        """Test that complete validation sanitizes filename"""
        file = UploadFile(
            filename="file<name>.pdf",
            file=BytesIO(b"content"),
            content_type="application/pdf"
        )
        
        result = validate_file(file)
        assert result == "file_name_.pdf"
        assert "<" not in result