"""
Tests for CLI-credential resolution and auth-source reporting.

Covers: the per-platform credentials path, read_cli_credentials() failure
modes, the client's resolution precedence (param -> env -> CLI store ->
actionable error), and the User-Agent auth field.
"""

import json
import sys
from pathlib import Path

import pytest

import brightdata.client as client_module
from brightdata.client import BrightDataClient
from brightdata.cli_credentials import _cli_credentials_path, read_cli_credentials
from brightdata.core.engine import AsyncEngine
from brightdata.exceptions import ValidationError

PARAM_TOKEN = "param_token_1234567890"
ENV_TOKEN = "env_token_1234567890"
CLI_TOKEN = "cli_token_1234567890"


@pytest.fixture
def no_env(monkeypatch):
    """Clear both token env vars (a repo .env may have populated them via dotenv)."""
    monkeypatch.delenv("BRIGHTDATA_API_TOKEN", raising=False)
    monkeypatch.delenv("BRIGHTDATA_API_KEY", raising=False)


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Point Path.home() at a temp dir so tests never touch the real CLI store."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


def _write_credentials(base: Path, content) -> Path:
    cred_dir = base / "brightdata-cli"
    cred_dir.mkdir(parents=True, exist_ok=True)
    path = cred_dir / "credentials.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content))
    return path


# ---------------------------------------------------------------------------
# Platform-specific credentials path
# ---------------------------------------------------------------------------


class TestCredentialsPath:
    def test_darwin(self, fake_home, monkeypatch):
        monkeypatch.setattr(sys, "platform", "darwin")
        expected = fake_home / "Library" / "Application Support" / "brightdata-cli"
        assert _cli_credentials_path() == expected / "credentials.json"

    def test_linux(self, fake_home, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        expected = fake_home / ".config" / "brightdata-cli"
        assert _cli_credentials_path() == expected / "credentials.json"

    def test_win32_with_appdata(self, fake_home, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        appdata = tmp_path / "Roaming"
        monkeypatch.setenv("APPDATA", str(appdata))
        assert _cli_credentials_path() == appdata / "brightdata-cli" / "credentials.json"

    def test_win32_without_appdata(self, fake_home, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.delenv("APPDATA", raising=False)
        expected = fake_home / "AppData" / "Roaming" / "brightdata-cli"
        assert _cli_credentials_path() == expected / "credentials.json"


# ---------------------------------------------------------------------------
# read_cli_credentials — happy path + every failure mode returns None
# ---------------------------------------------------------------------------


class TestReadCliCredentials:
    @pytest.fixture(autouse=True)
    def _linux(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")

    def test_valid_file(self, fake_home):
        _write_credentials(fake_home / ".config", {"api_key": CLI_TOKEN})
        assert read_cli_credentials() == CLI_TOKEN

    def test_key_is_trimmed(self, fake_home):
        _write_credentials(fake_home / ".config", {"api_key": f"  {CLI_TOKEN}  "})
        assert read_cli_credentials() == CLI_TOKEN

    def test_missing_file(self, fake_home):
        assert read_cli_credentials() is None

    def test_malformed_json(self, fake_home):
        _write_credentials(fake_home / ".config", "{not json")
        assert read_cli_credentials() is None

    def test_missing_api_key_field(self, fake_home):
        _write_credentials(fake_home / ".config", {"other": "x"})
        assert read_cli_credentials() is None

    def test_non_string_api_key(self, fake_home):
        _write_credentials(fake_home / ".config", {"api_key": 12345})
        assert read_cli_credentials() is None

    def test_empty_api_key(self, fake_home):
        _write_credentials(fake_home / ".config", {"api_key": "   "})
        assert read_cli_credentials() is None

    def test_config_json_is_never_read(self, fake_home):
        """Only credentials.json is consulted — config.json beside it is ignored."""
        cred_dir = fake_home / ".config" / "brightdata-cli"
        cred_dir.mkdir(parents=True)
        (cred_dir / "config.json").write_text(json.dumps({"api_key": "from_config"}))
        assert read_cli_credentials() is None


# ---------------------------------------------------------------------------
# Client resolution precedence: param -> env -> CLI -> error
# ---------------------------------------------------------------------------


class TestResolutionPrecedence:
    def test_param_wins_over_env_and_cli(self, monkeypatch):
        monkeypatch.setenv("BRIGHTDATA_API_TOKEN", ENV_TOKEN)
        monkeypatch.setattr(client_module, "read_cli_credentials", lambda: CLI_TOKEN)
        c = BrightDataClient(token=PARAM_TOKEN)
        assert c.token == PARAM_TOKEN
        assert c.auth_source == "param"

    def test_env_wins_over_cli(self, no_env, monkeypatch):
        monkeypatch.setenv("BRIGHTDATA_API_TOKEN", ENV_TOKEN)
        monkeypatch.setattr(client_module, "read_cli_credentials", lambda: CLI_TOKEN)
        c = BrightDataClient()
        assert c.token == ENV_TOKEN
        assert c.auth_source == "env"

    def test_alt_env_var(self, no_env, monkeypatch):
        monkeypatch.setenv("BRIGHTDATA_API_KEY", ENV_TOKEN)
        c = BrightDataClient()
        assert c.token == ENV_TOKEN
        assert c.auth_source == "env"

    def test_primary_env_var_beats_alt(self, no_env, monkeypatch):
        monkeypatch.setenv("BRIGHTDATA_API_TOKEN", ENV_TOKEN)
        monkeypatch.setenv("BRIGHTDATA_API_KEY", "other_token_1234567890")
        c = BrightDataClient()
        assert c.token == ENV_TOKEN

    def test_cli_fallback(self, no_env, monkeypatch):
        monkeypatch.setattr(client_module, "read_cli_credentials", lambda: CLI_TOKEN)
        c = BrightDataClient()
        assert c.token == CLI_TOKEN
        assert c.auth_source == "cli_credentials"

    def test_no_credentials_error_is_actionable(self, no_env, monkeypatch):
        monkeypatch.setattr(client_module, "read_cli_credentials", lambda: None)
        with pytest.raises(ValidationError) as exc_info:
            BrightDataClient()
        msg = str(exc_info.value)
        assert "brightdata login" in msg
        assert "BRIGHTDATA_API_TOKEN" in msg
        assert "https://brightdata.com/cp/api_keys" in msg

    def test_sync_client_inherits_resolution(self, no_env, monkeypatch):
        from brightdata.sync_client import SyncBrightDataClient

        monkeypatch.setattr(client_module, "read_cli_credentials", lambda: CLI_TOKEN)
        c = SyncBrightDataClient()
        assert c.token == CLI_TOKEN


# ---------------------------------------------------------------------------
# User-Agent auth-source reporting
# ---------------------------------------------------------------------------


class TestUserAgentAuthSource:
    @pytest.mark.parametrize("source", ["param", "env", "cli_credentials"])
    async def test_ua_carries_auth_source(self, source):
        engine = AsyncEngine(bearer_token="tok", auth_source=source)
        async with engine:
            ua = engine._session.headers["User-Agent"]
            assert ua.startswith("brightdata-sdk-python/")
            assert ua.endswith(f"(auth={source})")

    async def test_ua_without_auth_source(self):
        engine = AsyncEngine(bearer_token="tok")
        async with engine:
            ua = engine._session.headers["User-Agent"]
            assert ua.startswith("brightdata-sdk-python/")
            assert "(auth=" not in ua

    async def test_token_never_in_user_agent(self):
        engine = AsyncEngine(bearer_token="super_secret_token_value", auth_source="env")
        async with engine:
            assert "super_secret_token_value" not in engine._session.headers["User-Agent"]

    def test_client_wires_auth_source_into_engine(self):
        c = BrightDataClient(token=PARAM_TOKEN)
        assert c.engine._auth_source == "param"
        assert c.auth_source == "param"
