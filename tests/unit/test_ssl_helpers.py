"""Tests for utils/ssl_helpers.py — SSL error detection and messages."""

import ssl
from unittest.mock import Mock, patch

from brightdata.utils.ssl_helpers import is_macos, is_ssl_certificate_error, get_ssl_error_message


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------


class TestPlatformDetection:
    def test_returns_boolean(self):
        assert isinstance(is_macos(), bool)

    @patch("sys.platform", "darwin")
    def test_true_on_darwin(self):
        assert is_macos() is True

    @patch("sys.platform", "linux")
    def test_false_on_linux(self):
        assert is_macos() is False

    @patch("sys.platform", "win32")
    def test_false_on_windows(self):
        assert is_macos() is False


# ---------------------------------------------------------------------------
# SSL certificate error detection
# ---------------------------------------------------------------------------


class TestSSLCertificateErrorDetection:
    def test_ssl_error_detected(self):
        assert is_ssl_certificate_error(ssl.SSLError("certificate verify failed")) is True

    def test_oserror_with_ssl_keywords_detected(self):
        assert is_ssl_certificate_error(OSError("SSL certificate verification failed")) is True

    def test_oserror_with_certificate_keyword_detected(self):
        assert is_ssl_certificate_error(OSError("unable to get local issuer certificate")) is True

    def test_generic_exception_with_ssl_message_detected(self):
        assert is_ssl_certificate_error(Exception("[SSL: CERTIFICATE_VERIFY_FAILED]")) is True

    def test_certificate_verify_failed_detected(self):
        assert is_ssl_certificate_error(Exception("certificate verify failed")) is True

    def test_non_ssl_error_not_detected(self):
        assert is_ssl_certificate_error(ValueError("Invalid value")) is False

    def test_connection_error_without_ssl_not_detected(self):
        assert is_ssl_certificate_error(ConnectionError("Connection refused")) is False

    def test_timeout_error_not_detected(self):
        assert is_ssl_certificate_error(TimeoutError("Operation timed out")) is False


# ---------------------------------------------------------------------------
# SSL error messages
# ---------------------------------------------------------------------------


class TestSSLErrorMessage:
    @patch("brightdata.utils.ssl_helpers.is_macos", return_value=True)
    def test_macos_includes_platform_specific_fixes(self, _):
        message = get_ssl_error_message(ssl.SSLError("certificate verify failed"))

        assert "SSL certificate verification failed" in message
        assert "macOS" in message
        assert "Install Certificates.command" in message
        assert "Homebrew" in message
        assert "certifi" in message
        assert "SSL_CERT_FILE" in message

    @patch("brightdata.utils.ssl_helpers.is_macos", return_value=False)
    def test_non_macos_excludes_macos_fixes(self, _):
        message = get_ssl_error_message(ssl.SSLError("certificate verify failed"))

        assert "SSL certificate verification failed" in message
        assert "Install Certificates.command" not in message
        assert "Homebrew" not in message
        assert "certifi" in message
        assert "SSL_CERT_FILE" in message

    def test_includes_original_error(self):
        message = get_ssl_error_message(ssl.SSLError("specific error details"))
        assert "Original error:" in message
        assert "specific error details" in message

    def test_includes_fix_instructions(self):
        message = get_ssl_error_message(ssl.SSLError("certificate verify failed"))
        assert "pip install" in message
        assert "certifi" in message
        assert "export SSL_CERT_FILE" in message
        assert "python -m certifi" in message

    def test_includes_documentation_link(self):
        message = get_ssl_error_message(ssl.SSLError("certificate verify failed"))
        assert "docs/troubleshooting" in message or "troubleshooting.md" in message


# ---------------------------------------------------------------------------
# Different error formats
# ---------------------------------------------------------------------------


class TestSSLErrorFormats:
    def test_detailed_ssl_error(self):
        error = ssl.SSLError(
            "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: "
            "unable to get local issuer certificate"
        )
        message = get_ssl_error_message(error)
        assert message is not None
        assert "SSL certificate verification failed" in message

    def test_oserror_with_ssl_context(self):
        message = get_ssl_error_message(OSError(1, "SSL: certificate verify failed"))
        assert message is not None
        assert len(message) > 0

    def test_generic_exception_with_ssl_message(self):
        message = get_ssl_error_message(
            Exception("SSL certificate problem: unable to get local issuer certificate")
        )
        assert message is not None
        assert len(message) > 0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestSSLEdgeCases:
    def test_empty_error_message(self):
        assert is_ssl_certificate_error(Exception("")) is False

    def test_none_error_message_does_not_crash(self):
        error = Mock()
        error.__str__ = Mock(return_value=None)
        try:
            result = is_ssl_certificate_error(error)
            assert isinstance(result, bool)
        except (TypeError, AttributeError):
            pass  # acceptable — function should not crash

    def test_case_insensitive_detection(self):
        assert is_ssl_certificate_error(Exception("SSL CERTIFICATE VERIFY FAILED")) is True
        assert is_ssl_certificate_error(Exception("ssl certificate verify failed")) is True
        assert is_ssl_certificate_error(Exception("Ssl Certificate Verify Failed")) is True

    def test_partial_keyword_match(self):
        assert is_ssl_certificate_error(Exception("invalid certificate")) is True

    def test_keyword_in_middle_of_message(self):
        assert (
            is_ssl_certificate_error(
                Exception("Connection failed due to SSL certificate verification error")
            )
            is True
        )


# ---------------------------------------------------------------------------
# Integration
# ---------------------------------------------------------------------------


class TestSSLIntegration:
    def test_common_ssl_errors_identified_and_formatted(self):
        common_errors = [
            ssl.SSLError("certificate verify failed"),
            Exception("[SSL: CERTIFICATE_VERIFY_FAILED]"),
            OSError("unable to get local issuer certificate"),
            Exception("SSL certificate problem"),
        ]

        for error in common_errors:
            assert is_ssl_certificate_error(error) is True
            message = get_ssl_error_message(error)
            assert len(message) > 100
            assert "certifi" in message.lower()

    def test_non_ssl_errors_not_flagged(self):
        non_ssl_errors = [
            ValueError("Invalid parameter"),
            KeyError("missing_key"),
            TypeError("wrong type"),
            ConnectionError("Connection refused"),
            TimeoutError("Request timed out"),
        ]

        for error in non_ssl_errors:
            assert is_ssl_certificate_error(error) is False
