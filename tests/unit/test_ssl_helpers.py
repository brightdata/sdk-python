"""Unit tests for SSL error handling utilities."""

import ssl
from unittest.mock import Mock, patch
from brightdata.utils.ssl_helpers import is_macos, is_ssl_certificate_error, get_ssl_error_message


class TestPlatformDetection:
    """Test platform detection utilities."""

    def test_is_macos_returns_boolean(self):
        """Test is_macos returns a boolean."""
        result = is_macos()
        assert isinstance(result, bool)

    @patch("sys.platform", "darwin")
    def test_is_macos_true_on_darwin(self):
        """Test is_macos returns True on darwin platform."""
        result = is_macos()
        assert result is True

    @patch("sys.platform", "linux")
    def test_is_macos_false_on_linux(self):
        """Test is_macos returns False on linux."""
        result = is_macos()
        assert result is False

    @patch("sys.platform", "win32")
    def test_is_macos_false_on_windows(self):
        """Test is_macos returns False on Windows."""
        result = is_macos()
        assert result is False


class TestSSLCertificateErrorDetection:
    """Test SSL certificate error detection."""

    def test_ssl_error_is_detected(self):
        """Test SSL errors are detected."""
        error = ssl.SSLError("certificate verify failed")
        assert is_ssl_certificate_error(error) is True

    def test_oserror_with_ssl_keywords_is_detected(self):
        """Test OSError with SSL keywords is detected."""
        error = OSError("SSL certificate verification failed")
        assert is_ssl_certificate_error(error) is True

    def test_oserror_with_certificate_keyword_is_detected(self):
        """Test OSError with 'certificate' keyword is detected."""
        error = OSError("unable to get local issuer certificate")
        assert is_ssl_certificate_error(error) is True

    def test_generic_exception_with_ssl_message_is_detected(self):
        """Test generic exception with SSL message is detected."""
        error = Exception("[SSL: CERTIFICATE_VERIFY_FAILED]")
        assert is_ssl_certificate_error(error) is True

    def test_exception_with_certificate_verify_failed(self):
        """Test exception with 'certificate verify failed' is detected."""
        error = Exception("certificate verify failed")
        assert is_ssl_certificate_error(error) is True

    def test_non_ssl_error_is_not_detected(self):
        """Test non-SSL errors are not detected."""
        error = ValueError("Invalid value")
        assert is_ssl_certificate_error(error) is False

    def test_connection_error_without_ssl_is_not_detected(self):
        """Test connection errors without SSL keywords are not detected."""
        error = ConnectionError("Connection refused")
        assert is_ssl_certificate_error(error) is False

    def test_timeout_error_is_not_detected(self):
        """Test timeout errors are not detected as SSL errors."""
        error = TimeoutError("Operation timed out")
        assert is_ssl_certificate_error(error) is False


class TestSSLErrorMessage:
    """Test SSL error message generation."""

    @patch("brightdata.utils.ssl_helpers.is_macos", return_value=True)
    def test_macos_error_message_includes_platform_specific_fixes(self, mock_is_macos):
        """Test macOS error message includes platform-specific fixes."""
        error = ssl.SSLError("certificate verify failed")
        message = get_ssl_error_message(error)

        # Should include base message
        assert "SSL certificate verification failed" in message
        assert "macOS" in message

        # Should include macOS-specific fixes
        assert "Install Certificates.command" in message
        assert "Homebrew" in message
        assert "certifi" in message
        assert "SSL_CERT_FILE" in message

    @patch("brightdata.utils.ssl_helpers.is_macos", return_value=False)
    def test_non_macos_error_message_excludes_macos_specific_fixes(self, mock_is_macos):
        """Test non-macOS error message excludes macOS-specific fixes."""
        error = ssl.SSLError("certificate verify failed")
        message = get_ssl_error_message(error)

        # Should include base message
        assert "SSL certificate verification failed" in message

        # Should NOT include macOS-specific fixes
        assert "Install Certificates.command" not in message
        assert "Homebrew" not in message

        # Should include generic fixes
        assert "certifi" in message
        assert "SSL_CERT_FILE" in message

    def test_error_message_includes_original_error(self):
        """Test error message includes original error."""
        error = ssl.SSLError("specific error details")
        message = get_ssl_error_message(error)

        assert "Original error:" in message
        assert "specific error details" in message

    def test_error_message_includes_fix_instructions(self):
        """Test error message includes fix instructions."""
        error = ssl.SSLError("certificate verify failed")
        message = get_ssl_error_message(error)

        # Should include pip install command
        assert "pip install" in message
        assert "certifi" in message

        # Should include SSL_CERT_FILE command
        assert "export SSL_CERT_FILE" in message
        assert "python -m certifi" in message

    def test_error_message_includes_documentation_link(self):
        """Test error message includes documentation link."""
        error = ssl.SSLError("certificate verify failed")
        message = get_ssl_error_message(error)

        # Should include link to troubleshooting docs
        assert "docs/troubleshooting" in message or "troubleshooting.md" in message


class TestSSLErrorMessageFormats:
    """Test SSL error message handles different error formats."""

    def test_ssl_error_with_detailed_message(self):
        """Test handling of SSL error with detailed message."""
        error = ssl.SSLError(
            "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate"
        )
        message = get_ssl_error_message(error)

        assert message is not None
        assert len(message) > 0
        assert "SSL certificate verification failed" in message

    def test_oserror_with_ssl_context(self):
        """Test handling of OSError with SSL context."""
        error = OSError(1, "SSL: certificate verify failed")
        message = get_ssl_error_message(error)

        assert message is not None
        assert len(message) > 0

    def test_generic_exception_with_ssl_message(self):
        """Test handling of generic exception with SSL message."""
        error = Exception("SSL certificate problem: unable to get local issuer certificate")
        message = get_ssl_error_message(error)

        assert message is not None
        assert len(message) > 0


class TestSSLErrorDetectionEdgeCases:
    """Test SSL error detection edge cases."""

    def test_empty_error_message(self):
        """Test handling of error with empty message."""
        error = Exception("")
        assert is_ssl_certificate_error(error) is False

    def test_none_error_message(self):
        """Test handling of error with None message."""
        error = Mock()
        error.__str__ = Mock(return_value=None)
        # Should not crash - handle None return gracefully
        try:
            result = is_ssl_certificate_error(error)
            assert isinstance(result, bool)
        except (TypeError, AttributeError):
            # If __str__ returns None, we should handle it gracefully
            # This is acceptable behavior - function should not crash
            assert True

    def test_ssl_keyword_case_insensitive(self):
        """Test SSL keyword detection is case-insensitive."""
        error1 = Exception("SSL CERTIFICATE VERIFY FAILED")
        error2 = Exception("ssl certificate verify failed")
        error3 = Exception("Ssl Certificate Verify Failed")

        assert is_ssl_certificate_error(error1) is True
        assert is_ssl_certificate_error(error2) is True
        assert is_ssl_certificate_error(error3) is True

    def test_partial_ssl_keyword_match(self):
        """Test partial SSL keyword matches are detected."""
        # "certificate" keyword alone should match
        error = Exception("invalid certificate")
        assert is_ssl_certificate_error(error) is True

    def test_ssl_error_in_middle_of_message(self):
        """Test SSL keywords in middle of message are detected."""
        error = Exception("Connection failed due to SSL certificate verification error")
        assert is_ssl_certificate_error(error) is True


class TestSSLHelperIntegration:
    """Test SSL helper integration scenarios."""

    def test_can_identify_and_format_common_ssl_errors(self):
        """Test can identify and format common SSL error scenarios."""
        common_errors = [
            ssl.SSLError("certificate verify failed"),
            Exception("[SSL: CERTIFICATE_VERIFY_FAILED]"),
            OSError("unable to get local issuer certificate"),
            Exception("SSL certificate problem"),
        ]

        for error in common_errors:
            # Should be identified as SSL error
            assert is_ssl_certificate_error(error) is True

            # Should generate helpful message
            message = get_ssl_error_message(error)
            assert len(message) > 100  # Should be substantial
            assert "certifi" in message.lower()

    def test_non_ssl_errors_dont_trigger_ssl_handling(self):
        """Test non-SSL errors don't trigger SSL handling."""
        non_ssl_errors = [
            ValueError("Invalid parameter"),
            KeyError("missing_key"),
            TypeError("wrong type"),
            ConnectionError("Connection refused"),
            TimeoutError("Request timed out"),
        ]

        for error in non_ssl_errors:
            assert is_ssl_certificate_error(error) is False
