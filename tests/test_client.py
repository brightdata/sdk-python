"""
Comprehensive tests for the Bright Data SDK client.

This test suite covers:
- Client initialization with API tokens (from parameter and environment)
- API token validation and error handling for missing tokens
- Zone configuration (default and custom zone names)
- URL validation in scrape method (scheme requirement)
- Search query validation (empty query handling)
- Search engine validation (unsupported engine handling)

All tests are designed to run without requiring real API tokens by:
- Using sufficiently long test tokens to pass validation
- Mocking zone management to avoid network calls
- Testing validation logic and error messages
"""

<<<<<<< HEAD
import pytest
import os
from unittest.mock import patch

from brightdata import bdclient
=======
import os
import pytest
from brightdata import bdclient
from unittest.mock import patch
>>>>>>> old/main
from brightdata.exceptions import ValidationError


class TestBdClient:
    """Test cases for the main bdclient class"""
    
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def test_client_init_with_token(self, mock_zones):
        """Test client initialization with API token"""
        with patch.dict(os.environ, {}, clear=True):
            client = bdclient(api_token="valid_test_token_12345678", auto_create_zones=False)
            assert client.api_token == "valid_test_token_12345678"
    
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def test_client_init_from_env(self, mock_zones):
        """Test client initialization from environment variable"""
        with patch.dict(os.environ, {"BRIGHTDATA_API_TOKEN": "valid_env_token_12345678"}):
            client = bdclient(auto_create_zones=False)
            assert client.api_token == "valid_env_token_12345678"
    
    def test_client_init_no_token_raises_error(self):
        """Test that missing API token raises ValidationError"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('dotenv.load_dotenv'):
                with pytest.raises(ValidationError, match="API token is required"):
                    bdclient()
    
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def test_client_zone_defaults(self, mock_zones):
        """Test default zone configurations"""
        with patch.dict(os.environ, {}, clear=True):
            client = bdclient(api_token="valid_test_token_12345678", auto_create_zones=False)
            assert client.web_unlocker_zone == "sdk_unlocker"
            assert client.serp_zone == "sdk_serp"
    
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def test_client_custom_zones(self, mock_zones):
        """Test custom zone configuration"""
        with patch.dict(os.environ, {}, clear=True):
            client = bdclient(
                api_token="valid_test_token_12345678",
                web_unlocker_zone="custom_unlocker",
                serp_zone="custom_serp",
                auto_create_zones=False
            )
            assert client.web_unlocker_zone == "custom_unlocker"
            assert client.serp_zone == "custom_serp"


class TestClientMethods:
    """Test cases for client methods with mocked responses"""
    
    @pytest.fixture
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def client(self, mock_zones):
        """Create a test client with mocked validation"""
        with patch.dict(os.environ, {}, clear=True):
            client = bdclient(api_token="valid_test_token_12345678", auto_create_zones=False)
            return client
    
    def test_scrape_single_url_validation(self, client):
        """Test URL validation in scrape method"""
        with pytest.raises(ValidationError, match="URL must include a scheme"):
            client.scrape("not_a_url")
    
    def test_search_empty_query_validation(self, client):
        """Test query validation in search method"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            client.search("")
    
    def test_search_unsupported_engine(self, client):
        """Test unsupported search engine validation"""
        with pytest.raises(ValidationError, match="Invalid search engine"):
            client.search("test query", search_engine="invalid_engine")
    
    def test_search_with_parse_parameter(self, client, monkeypatch):
        """Test search with parse parameter adds brd_json=1 to URL"""
        # Mock the session.post method to capture the request
        captured_request = {}
        
        def mock_post(*args, **kwargs):
            captured_request.update(kwargs)
            from unittest.mock import Mock
            response = Mock()
            response.status_code = 200
            response.text = "mocked html response"
            return response
        
        monkeypatch.setattr(client.search_api.session, 'post', mock_post)
        
        result = client.search("test query", parse=True)
        
        # Verify the request was made with correct URL containing &brd_json=1
        request_data = captured_request.get('json', {})
        assert "&brd_json=1" in request_data["url"]

<<<<<<< HEAD

if __name__ == "__main__":
    pytest.main([__file__])
=======
class TestClientSearchGPT:
    """Tests for the client.search_gpt() function"""

    @pytest.fixture
    @patch('brightdata.utils.zone_manager.ZoneManager.ensure_required_zones')
    def client(self, mock_zones):
        """Create a test client with mocked validation"""
        with patch.dict(os.environ, {}, clear=True):
            client = bdclient(api_token="valid_test_token_12345678", auto_create_zones=False)
            return client

    # VALIDATION TESTS 

    def test_prompt_required(self, client):
        """Ensure ValidationError is raised when prompt is missing"""
        with pytest.raises(ValidationError, match="prompt is required"):
            client.search_gpt(prompt=None)

    def test_invalid_country_format(self, client):
        """Reject invalid country codes"""
        with pytest.raises(ValidationError, match="must be 2-letter code"):
            client.search_gpt(prompt="hi", country="USA")

    def test_websearch_bool_validation(self, client):
        """Reject invalid webSearch parameter type"""
        with pytest.raises(ValidationError, match="must be a boolean or list of booleans"):
            client.search_gpt(prompt="hi", webSearch="yes")

    # PARAMETER NORMALIZATION 
    
    def test_normalizes_single_values_to_list(self, client, monkeypatch):
        """Convert single parameters to list form"""
        # Mock the session.post to intercept and provide dummy response
        def dummy_post(url, json=None, timeout=None):
            from unittest.mock import Mock
            r = Mock()
            r.status_code = 200
            # Build dummy response with normalized lists
            if isinstance(json, list):
                prompts = [item.get('prompt', '') for item in json]
                countries = [item.get('country', '') for item in json]
                sec_prompts = [item.get('additional_prompt', '') for item in json]
                web_searches = [item.get('web_search', False) for item in json]
            else:
                prompts = [json.get('prompt', '')]
                countries = [json.get('country', '')]
                sec_prompts = [json.get('additional_prompt', '')]
                web_searches = [json.get('web_search', False)]
            r.json.return_value = {
                'prompt': prompts,
                'country': countries,
                'secondaryPrompt': sec_prompts,
                'webSearch': web_searches
            }
            return r
        monkeypatch.setattr(client.search_api.session, 'post', dummy_post)
        result = client.search_gpt(
            prompt="hello",
            country="US",
            secondaryPrompt="follow up",
            webSearch=False,
            sync=True
        )
        # The internal normalized payload should contain lists
        assert isinstance(result["prompt"], list)
        assert isinstance(result["country"], list)
        assert isinstance(result["secondaryPrompt"], list)
        assert isinstance(result["webSearch"], list)

    # MOCKED API CALL TESTS 
    
    def test_sync_request_success(self, client, monkeypatch):
        """Ensure sync request returns expected payload"""
        mock_response = {"status": "ok", "data": "result"}
        captured_payload = {}

        def mock_post(url, json=None, timeout=None):
            captured_payload.update(json or {})
            from unittest.mock import Mock
            r = Mock()
            r.status_code = 200
            r.json.return_value = mock_response
            return r

        monkeypatch.setattr(client.search_api.session, "post", mock_post)

        response = client.search_gpt(prompt="Hello", country="US", sync=True)
        assert response == mock_response
        assert captured_payload["url"] == "https://chatgpt.com"
        assert "prompt" in captured_payload
        assert "country" in captured_payload

    def test_async_request_timeout(self, client, monkeypatch):
        """Ensure async mode uses correct timeout"""
        captured_args = {}

        def mock_post(url, json=None, timeout=None):
            captured_args["timeout"] = timeout
            from unittest.mock import Mock
            r = Mock()
            r.status_code = 200
            r.json.return_value = {"id": "s_testid"}
            return r

        monkeypatch.setattr(client.search_api.session, "post", mock_post)

        client.search_gpt(prompt="Async test", sync=False)
        assert captured_args["timeout"] == 30  # default async timeout

    # ERROR AND RETRY HANDLING

    def test_retry_on_failure(self, client, monkeypatch):
        """Test that request is retried on temporary failure"""
        call_count = {"n": 0}

        def mock_post(url, json=None, timeout=None):
            call_count["n"] += 1
            from unittest.mock import Mock
            r = Mock()
            r.status_code = 500 if call_count["n"] == 1 else 200
            r.json.return_value = {"ok": True}
            return r

        monkeypatch.setattr(client.search_api.session, "post", mock_post)
        result = client.search_gpt(prompt="retry", sync=True)
        assert result["ok"] is True
        assert call_count["n"] == 2  # retried once

    def test_raises_error_after_max_retries(self, client, monkeypatch):
        """Ensure error is raised after exceeding retries"""
        def mock_post(url, json=None, timeout=None):
            from unittest.mock import Mock
            r = Mock()
            r.status_code = 500
            r.json.return_value = {"error": "server error"}
            return r

        monkeypatch.setattr(client.search_api.session, "post", mock_post)
        with pytest.raises(RuntimeError, match="Failed after retries"):
            client.search_gpt(prompt="fail test", sync=True)
>>>>>>> old/main
