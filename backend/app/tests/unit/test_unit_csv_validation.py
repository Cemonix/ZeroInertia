"""
Unit tests for CSV file size validation.

Tests the file size validation functionality added to prevent
memory exhaustion and denial of service attacks.
"""

import pytest

from app.core.exceptions import BadRequestException
from app.services.media_service.csv_import_service import validate_csv_file_size


class TestCSVFileSizeValidation:
    """Test CSV file size validation."""

    def test_valid_file_size_small(self) -> None:
        """Test that small files pass validation."""
        # 1 MB file
        file_size = 1 * 1024 * 1024
        # Should not raise an exception
        validate_csv_file_size(file_size)

    def test_valid_file_size_at_limit(self) -> None:
        """Test that files exactly at the limit pass validation."""
        # Default limit is 10 MB
        file_size = 10 * 1024 * 1024
        # Should not raise an exception
        validate_csv_file_size(file_size)

    def test_invalid_file_size_exceeds_limit(self) -> None:
        """Test that files exceeding the limit raise BadRequestException."""
        # 11 MB file (exceeds default 10 MB limit)
        file_size = 11 * 1024 * 1024

        with pytest.raises(BadRequestException) as exc_info:
            validate_csv_file_size(file_size)

        assert "exceeds maximum allowed size" in str(exc_info.value.message)
        assert "11.00 MB" in str(exc_info.value.message)
        assert "10 MB" in str(exc_info.value.message)

    def test_invalid_file_size_very_large(self) -> None:
        """Test that very large files are rejected."""
        # 100 MB file
        file_size = 100 * 1024 * 1024

        with pytest.raises(BadRequestException) as exc_info:
            validate_csv_file_size(file_size)

        assert "exceeds maximum allowed size" in str(exc_info.value.message)

    def test_zero_byte_file(self) -> None:
        """Test that zero-byte files pass validation (caught by other checks)."""
        file_size = 0
        # Should not raise an exception (empty file validation is elsewhere)
        validate_csv_file_size(file_size)
