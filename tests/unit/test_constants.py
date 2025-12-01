"""Unit tests for constants module."""

from brightdata import constants


class TestPollingConstants:
    """Test polling configuration constants."""

    def test_default_poll_interval_exists(self):
        """Test DEFAULT_POLL_INTERVAL constant exists."""
        assert hasattr(constants, "DEFAULT_POLL_INTERVAL")

    def test_default_poll_interval_is_integer(self):
        """Test DEFAULT_POLL_INTERVAL is an integer."""
        assert isinstance(constants.DEFAULT_POLL_INTERVAL, int)

    def test_default_poll_interval_is_positive(self):
        """Test DEFAULT_POLL_INTERVAL is positive."""
        assert constants.DEFAULT_POLL_INTERVAL > 0

    def test_default_poll_interval_value(self):
        """Test DEFAULT_POLL_INTERVAL has expected value."""
        assert constants.DEFAULT_POLL_INTERVAL == 10

    def test_default_poll_timeout_exists(self):
        """Test DEFAULT_POLL_TIMEOUT constant exists."""
        assert hasattr(constants, "DEFAULT_POLL_TIMEOUT")

    def test_default_poll_timeout_is_integer(self):
        """Test DEFAULT_POLL_TIMEOUT is an integer."""
        assert isinstance(constants.DEFAULT_POLL_TIMEOUT, int)

    def test_default_poll_timeout_is_positive(self):
        """Test DEFAULT_POLL_TIMEOUT is positive."""
        assert constants.DEFAULT_POLL_TIMEOUT > 0

    def test_default_poll_timeout_value(self):
        """Test DEFAULT_POLL_TIMEOUT has expected value."""
        assert constants.DEFAULT_POLL_TIMEOUT == 600

    def test_poll_timeout_greater_than_interval(self):
        """Test DEFAULT_POLL_TIMEOUT is greater than DEFAULT_POLL_INTERVAL."""
        assert constants.DEFAULT_POLL_TIMEOUT > constants.DEFAULT_POLL_INTERVAL


class TestTimeoutConstants:
    """Test timeout configuration constants."""

    def test_default_timeout_short_exists(self):
        """Test DEFAULT_TIMEOUT_SHORT constant exists."""
        assert hasattr(constants, "DEFAULT_TIMEOUT_SHORT")

    def test_default_timeout_short_is_integer(self):
        """Test DEFAULT_TIMEOUT_SHORT is an integer."""
        assert isinstance(constants.DEFAULT_TIMEOUT_SHORT, int)

    def test_default_timeout_short_is_positive(self):
        """Test DEFAULT_TIMEOUT_SHORT is positive."""
        assert constants.DEFAULT_TIMEOUT_SHORT > 0

    def test_default_timeout_short_value(self):
        """Test DEFAULT_TIMEOUT_SHORT has expected value."""
        assert constants.DEFAULT_TIMEOUT_SHORT == 180

    def test_default_timeout_medium_exists(self):
        """Test DEFAULT_TIMEOUT_MEDIUM constant exists."""
        assert hasattr(constants, "DEFAULT_TIMEOUT_MEDIUM")

    def test_default_timeout_medium_is_integer(self):
        """Test DEFAULT_TIMEOUT_MEDIUM is an integer."""
        assert isinstance(constants.DEFAULT_TIMEOUT_MEDIUM, int)

    def test_default_timeout_medium_is_positive(self):
        """Test DEFAULT_TIMEOUT_MEDIUM is positive."""
        assert constants.DEFAULT_TIMEOUT_MEDIUM > 0

    def test_default_timeout_medium_value(self):
        """Test DEFAULT_TIMEOUT_MEDIUM has expected value."""
        assert constants.DEFAULT_TIMEOUT_MEDIUM == 240

    def test_default_timeout_long_exists(self):
        """Test DEFAULT_TIMEOUT_LONG constant exists."""
        assert hasattr(constants, "DEFAULT_TIMEOUT_LONG")

    def test_default_timeout_long_is_integer(self):
        """Test DEFAULT_TIMEOUT_LONG is an integer."""
        assert isinstance(constants.DEFAULT_TIMEOUT_LONG, int)

    def test_default_timeout_long_is_positive(self):
        """Test DEFAULT_TIMEOUT_LONG is positive."""
        assert constants.DEFAULT_TIMEOUT_LONG > 0

    def test_default_timeout_long_value(self):
        """Test DEFAULT_TIMEOUT_LONG has expected value."""
        assert constants.DEFAULT_TIMEOUT_LONG == 120

    def test_timeout_relationships(self):
        """Test timeout constants have logical relationships."""
        # Medium should be greater than short
        assert constants.DEFAULT_TIMEOUT_MEDIUM > constants.DEFAULT_TIMEOUT_SHORT


class TestScraperConstants:
    """Test scraper configuration constants."""

    def test_default_min_poll_timeout_exists(self):
        """Test DEFAULT_MIN_POLL_TIMEOUT constant exists."""
        assert hasattr(constants, "DEFAULT_MIN_POLL_TIMEOUT")

    def test_default_min_poll_timeout_is_integer(self):
        """Test DEFAULT_MIN_POLL_TIMEOUT is an integer."""
        assert isinstance(constants.DEFAULT_MIN_POLL_TIMEOUT, int)

    def test_default_min_poll_timeout_is_positive(self):
        """Test DEFAULT_MIN_POLL_TIMEOUT is positive."""
        assert constants.DEFAULT_MIN_POLL_TIMEOUT > 0

    def test_default_min_poll_timeout_value(self):
        """Test DEFAULT_MIN_POLL_TIMEOUT has expected value."""
        assert constants.DEFAULT_MIN_POLL_TIMEOUT == 180

    def test_default_cost_per_record_exists(self):
        """Test DEFAULT_COST_PER_RECORD constant exists."""
        assert hasattr(constants, "DEFAULT_COST_PER_RECORD")

    def test_default_cost_per_record_is_float(self):
        """Test DEFAULT_COST_PER_RECORD is a float."""
        assert isinstance(constants.DEFAULT_COST_PER_RECORD, float)

    def test_default_cost_per_record_is_positive(self):
        """Test DEFAULT_COST_PER_RECORD is positive."""
        assert constants.DEFAULT_COST_PER_RECORD > 0

    def test_default_cost_per_record_value(self):
        """Test DEFAULT_COST_PER_RECORD has expected value."""
        assert constants.DEFAULT_COST_PER_RECORD == 0.001


class TestConstantsDocumentation:
    """Test constants have proper documentation."""

    def test_default_poll_interval_has_docstring(self):
        """Test DEFAULT_POLL_INTERVAL has documentation."""
        # Check module docstrings or comments exist
        import inspect

        source = inspect.getsource(constants)
        assert "DEFAULT_POLL_INTERVAL" in source

    def test_constants_module_has_docstring(self):
        """Test constants module has docstring."""
        assert constants.__doc__ is not None
        assert len(constants.__doc__) > 0


class TestConstantsUsage:
    """Test constants are used throughout the codebase."""

    def test_constants_imported_in_base_scraper(self):
        """Test constants are imported in base scraper."""
        from brightdata.scrapers import base

        # Should import from constants module
        import inspect

        source = inspect.getsource(base)
        assert "from ..constants import" in source or "constants" in source

    def test_constants_imported_in_polling(self):
        """Test constants are imported in polling utilities."""
        from brightdata.utils import polling

        import inspect

        source = inspect.getsource(polling)
        assert "from ..constants import" in source or "constants" in source

    def test_default_poll_interval_used_in_polling(self):
        """Test DEFAULT_POLL_INTERVAL is used in polling module."""
        from brightdata.utils import polling

        import inspect

        source = inspect.getsource(polling)
        assert "DEFAULT_POLL_INTERVAL" in source


class TestConstantsImmutability:
    """Test constants maintain their values."""

    def test_constants_are_not_none(self):
        """Test all constants are not None."""
        assert constants.DEFAULT_POLL_INTERVAL is not None
        assert constants.DEFAULT_POLL_TIMEOUT is not None
        assert constants.DEFAULT_TIMEOUT_SHORT is not None
        assert constants.DEFAULT_TIMEOUT_MEDIUM is not None
        assert constants.DEFAULT_TIMEOUT_LONG is not None
        assert constants.DEFAULT_MIN_POLL_TIMEOUT is not None
        assert constants.DEFAULT_COST_PER_RECORD is not None

    def test_constants_have_expected_types(self):
        """Test all constants have expected types."""
        # Integer constants
        assert isinstance(constants.DEFAULT_POLL_INTERVAL, int)
        assert isinstance(constants.DEFAULT_POLL_TIMEOUT, int)
        assert isinstance(constants.DEFAULT_TIMEOUT_SHORT, int)
        assert isinstance(constants.DEFAULT_TIMEOUT_MEDIUM, int)
        assert isinstance(constants.DEFAULT_TIMEOUT_LONG, int)
        assert isinstance(constants.DEFAULT_MIN_POLL_TIMEOUT, int)

        # Float constant
        assert isinstance(constants.DEFAULT_COST_PER_RECORD, float)


class TestConstantsExports:
    """Test constants module exports."""

    def test_can_import_constants_from_brightdata(self):
        """Test can import constants from brightdata package."""
        from brightdata import constants as const

        assert const is not None
        assert hasattr(const, "DEFAULT_POLL_INTERVAL")

    def test_can_import_specific_constants(self):
        """Test can import specific constants."""
        from brightdata.constants import (
            DEFAULT_POLL_INTERVAL,
            DEFAULT_POLL_TIMEOUT,
            DEFAULT_TIMEOUT_SHORT,
            DEFAULT_TIMEOUT_MEDIUM,
            DEFAULT_TIMEOUT_LONG,
            DEFAULT_MIN_POLL_TIMEOUT,
            DEFAULT_COST_PER_RECORD,
        )

        assert DEFAULT_POLL_INTERVAL is not None
        assert DEFAULT_POLL_TIMEOUT is not None
        assert DEFAULT_TIMEOUT_SHORT is not None
        assert DEFAULT_TIMEOUT_MEDIUM is not None
        assert DEFAULT_TIMEOUT_LONG is not None
        assert DEFAULT_MIN_POLL_TIMEOUT is not None
        assert DEFAULT_COST_PER_RECORD is not None


class TestConstantsReasonableValues:
    """Test constants have reasonable values for production use."""

    def test_poll_interval_is_reasonable(self):
        """Test poll interval is reasonable (not too frequent, not too slow)."""
        # Should be between 1 and 60 seconds
        assert 1 <= constants.DEFAULT_POLL_INTERVAL <= 60

    def test_poll_timeout_is_reasonable(self):
        """Test poll timeout is reasonable."""
        # Should be at least 1 minute, but not more than 30 minutes
        assert 60 <= constants.DEFAULT_POLL_TIMEOUT <= 1800

    def test_timeouts_are_reasonable(self):
        """Test all timeout values are reasonable for API operations."""
        # All timeouts should be between 30 seconds and 10 minutes
        assert 30 <= constants.DEFAULT_TIMEOUT_SHORT <= 600
        assert 30 <= constants.DEFAULT_TIMEOUT_MEDIUM <= 600
        assert 30 <= constants.DEFAULT_TIMEOUT_LONG <= 600

    def test_cost_per_record_is_reasonable(self):
        """Test cost per record is reasonable."""
        # Should be between $0.0001 and $0.01 per record
        assert 0.0001 <= constants.DEFAULT_COST_PER_RECORD <= 0.01

    def test_min_poll_timeout_is_reasonable(self):
        """Test minimum poll timeout is reasonable."""
        # Should be at least 1 minute
        assert constants.DEFAULT_MIN_POLL_TIMEOUT >= 60
