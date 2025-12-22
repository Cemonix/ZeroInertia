"""
Integration tests for CSV export with injection prevention.

Tests that CSV exports properly sanitize potentially dangerous values
that could be interpreted as formulas in spreadsheet applications.
"""

from app.models.media import Book
from app.services.media_service.csv_export_service import export_books_csv


class TestCSVExportInjectionPrevention:
    """Test CSV export with formula injection prevention."""

    def test_export_books_with_formula_in_title(self) -> None:
        """Test that books with formula characters in title are sanitized."""
        book = Book(
            id="00000000-0000-0000-0000-000000000001",
            title="=1+1",
            creator="Test Author",
            status="completed",
            is_audiobook=False,
            user_id="00000000-0000-0000-0000-000000000001",
        )

        csv_output = export_books_csv([book])

        # Check that the title is sanitized
        assert "'=1+1" in csv_output
        # Original dangerous value should not appear without sanitization
        lines = csv_output.split("\n")
        assert len(lines) >= 2
        data_line = lines[1]
        assert data_line.startswith("'=1+1")

    def test_export_books_with_formula_in_notes(self) -> None:
        """Test that books with formula characters in notes are sanitized."""
        book = Book(
            id="00000000-0000-0000-0000-000000000001",
            title="Safe Title",
            creator="Test Author",
            status="completed",
            is_audiobook=False,
            notes="=cmd|'/c calc'!A1",
            user_id="00000000-0000-0000-0000-000000000001",
        )

        csv_output = export_books_csv([book])

        # Check that notes are sanitized
        assert "'=cmd" in csv_output

    def test_export_books_with_multiple_dangerous_values(self) -> None:
        """Test export with multiple fields containing dangerous characters."""
        books = [
            Book(
                id="00000000-0000-0000-0000-000000000001",
                title="=SUM(A1:A10)",
                creator="+HYPERLINK",
                status="completed",
                is_audiobook=False,
                notes="@formula",
                user_id="00000000-0000-0000-0000-000000000001",
            ),
            Book(
                id="00000000-0000-0000-0000-000000000002",
                title="-1+1",
                creator="Safe Author",
                status="reading",
                is_audiobook=True,
                notes="\t=dangerous",
                user_id="00000000-0000-0000-0000-000000000001",
            ),
        ]

        csv_output = export_books_csv(books)

        # All dangerous values should be sanitized
        assert "'=SUM" in csv_output
        assert "'+HYPERLINK" in csv_output
        assert "'@formula" in csv_output
        assert "'-1+1" in csv_output
        assert "'\t=" in csv_output

    def test_export_books_with_safe_values(self) -> None:
        """Test that safe values are not modified."""
        book = Book(
            id="00000000-0000-0000-0000-000000000001",
            title="Normal Book Title",
            creator="John Doe",
            status="completed",
            is_audiobook=False,
            notes="This is a safe note with email@domain.com",
            user_id="00000000-0000-0000-0000-000000000001",
        )

        csv_output = export_books_csv([book])

        # Safe values should not have the sanitization prefix
        lines = csv_output.split("\n")
        data_line = lines[1]
        # Should not start with single quote
        assert not data_line.startswith("'Normal")
        # Email in middle should be fine
        assert "email@domain.com" in csv_output

    def test_export_preserves_csv_structure(self) -> None:
        """Test that CSV structure is preserved after sanitization."""
        book = Book(
            id="00000000-0000-0000-0000-000000000001",
            title="=Dangerous",
            creator="Author",
            status="completed",
            is_audiobook=False,
            user_id="00000000-0000-0000-0000-000000000001",
        )

        csv_output = export_books_csv([book])
        lines = csv_output.split("\n")

        # Should have header + 1 data row + empty line
        assert len(lines) >= 2

        # Header should be intact
        header = lines[0]
        assert "title" in header
        assert "creator" in header
        assert "status" in header

        # Verify basic structure and content
        # Note: csv module handles quoting, so we just verify basic structure
        assert "Dangerous" in csv_output  # The actual value is there
        assert "Author" in csv_output
        assert "completed" in csv_output
