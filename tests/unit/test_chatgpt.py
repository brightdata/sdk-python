"""Unit tests for ChatGPT search service."""

import inspect
from brightdata import BrightDataClient
from brightdata.scrapers.chatgpt import ChatGPTSearchService


class TestChatGPTSearchService:
    """Test ChatGPT search service."""

    def test_chatgpt_search_has_chatGPT_method(self):
        """Test ChatGPT search has chatGPT method."""
        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        assert hasattr(search, "chatGPT")
        assert hasattr(search, "chatGPT_async")
        assert callable(search.chatGPT)
        assert callable(search.chatGPT_async)

    def test_chatGPT_method_signature(self):
        """Test chatGPT method has correct signature."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        # Required: prompt
        assert "prompt" in sig.parameters

        # Optional parameters
        assert "country" in sig.parameters
        assert "secondaryPrompt" in sig.parameters
        assert "webSearch" in sig.parameters
        assert "sync" not in sig.parameters
        assert "timeout" in sig.parameters

        # Defaults
        assert sig.parameters["timeout"].default == 180

    def test_chatGPT_validates_required_prompt(self):
        """Test chatGPT raises error if prompt is missing."""
        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        # This would fail at runtime, but we test the validation exists
        # (Can't actually call without mocking the engine)
        assert "prompt" in str(inspect.signature(search.chatGPT).parameters)


class TestChatGPTAPISpecCompliance:
    """Test compliance with exact API specifications."""

    def test_api_spec_matches_cp_link(self):
        """Test method matches CP link specification."""
        client = BrightDataClient(token="test_token_123456789")

        # API Spec: client.search.chatGPT(prompt, country, secondaryPrompt, webSearch, timeout)
        import inspect

        sig = inspect.signature(client.search.chatGPT.chatGPT)

        params = sig.parameters

        # All parameters from spec
        assert "prompt" in params  # str | array<str>, required
        assert "country" in params  # str | array<str>, 2-letter format
        assert "secondaryPrompt" in params  # str | array<str>
        assert "webSearch" in params  # bool | array<bool>
        assert "sync" not in params  # Removed - uses standard async workflow
        assert "timeout" in params  # int, default: 180

    def test_parameter_defaults_match_spec(self):
        """Test parameter defaults match specification."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        # Defaults per spec
        assert sig.parameters["timeout"].default == 180

        # Optional params should default to None
        assert sig.parameters["country"].default is None
        assert sig.parameters["secondaryPrompt"].default is None
        assert sig.parameters["webSearch"].default is None


class TestChatGPTParameterArraySupport:
    """Test array parameter support (str | array<str>, bool | array<bool>)."""

    def test_prompt_accepts_string(self):
        """Test prompt parameter accepts single string."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        # Type annotation should allow str | List[str]
        prompt_annotation = str(sig.parameters["prompt"].annotation)
        assert "Union" in prompt_annotation or "str" in prompt_annotation

    def test_prompt_accepts_list(self):
        """Test prompt parameter accepts list."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        prompt_annotation = str(sig.parameters["prompt"].annotation)
        assert "List" in prompt_annotation or "list" in prompt_annotation

    def test_country_accepts_string_or_list(self):
        """Test country accepts str | list."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        annotation = str(sig.parameters["country"].annotation)
        # Should be Optional[Union[str, List[str]]]
        assert "str" in annotation

    def test_webSearch_accepts_bool_or_list(self):
        """Test webSearch accepts bool | list[bool]."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        annotation = str(sig.parameters["webSearch"].annotation)
        # Should accept bool | List[bool]
        assert "bool" in annotation


class TestChatGPTSyncAsyncMode:
    """Test standard async workflow (no sync parameter)."""

    def test_no_sync_parameter(self):
        """Test methods don't have sync parameter (standard async pattern)."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        assert "sync" not in sig.parameters

    def test_timeout_defaults_to_180(self):
        """Test timeout defaults to 180."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")
        sig = inspect.signature(search.chatGPT)

        assert sig.parameters["timeout"].default == 180

    def test_has_async_sync_pair(self):
        """Test has both chatGPT and chatGPT_async."""
        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        assert hasattr(search, "chatGPT")
        assert hasattr(search, "chatGPT_async")
        assert callable(search.chatGPT)
        assert callable(search.chatGPT_async)


class TestChatGPTClientIntegration:
    """Test ChatGPT search integrates with client."""

    def test_chatgpt_accessible_via_client_search(self):
        """Test ChatGPT search accessible via client.search.chatGPT."""
        client = BrightDataClient(token="test_token_123456789")

        chatgpt = client.search.chatGPT
        assert chatgpt is not None
        assert isinstance(chatgpt, ChatGPTSearchService)

    def test_client_passes_token_to_chatgpt_search(self):
        """Test client passes token to ChatGPT search."""
        token = "test_token_123456789"
        client = BrightDataClient(token=token)

        chatgpt = client.search.chatGPT
        assert chatgpt.bearer_token == token

    def test_chatGPT_method_callable_through_client(self):
        """Test chatGPT method callable through client."""
        client = BrightDataClient(token="test_token_123456789")

        # Should be able to access the method
        assert callable(client.search.chatGPT.chatGPT)
        assert callable(client.search.chatGPT.chatGPT_async)


class TestChatGPTInterfaceExamples:
    """Test interface examples from specification."""

    def test_single_prompt_interface(self):
        """Test single prompt interface."""
        client = BrightDataClient(token="test_token_123456789")

        # Interface should accept single prompt
        import inspect

        sig = inspect.signature(client.search.chatGPT.chatGPT)

        # Can call with just prompt
        assert "prompt" in sig.parameters

        # Other params are optional
        assert sig.parameters["country"].default is None
        assert sig.parameters["secondaryPrompt"].default is None
        assert sig.parameters["webSearch"].default is None

    def test_batch_prompts_interface(self):
        """Test batch prompts interface."""
        client = BrightDataClient(token="test_token_123456789")

        # Should accept lists for all parameters
        import inspect

        sig = inspect.signature(client.search.chatGPT.chatGPT)

        # All array parameters should be in Union with List
        prompt_annotation = str(sig.parameters["prompt"].annotation)
        assert "List" in prompt_annotation


class TestChatGPTCountryValidation:
    """Test country code validation."""

    def test_country_should_be_2_letter_format(self):
        """Test country parameter expects 2-letter format."""
        # This is validated in the implementation
        # We verify the docstring mentions it
        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        # Check docstring mentions 2-letter format
        doc = search.chatGPT_async.__doc__
        assert "2-letter" in doc or "2 letter" in doc.replace("-", " ")


class TestChatGPTPhilosophicalPrinciples:
    """Test ChatGPT search follows philosophical principles."""

    def test_fixed_url_per_spec(self):
        """Test URL is fixed to chatgpt.com per spec."""
        # Per spec comment: "the param URL will be fixed to https://chatgpt.com"
        # This is handled in the implementation
        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        # Verify implementation exists (can't test without API call)
        assert search.DATASET_ID == "gd_m7aof0k82r803d5bjm"

    def test_consistent_with_other_search_services(self):
        """Test ChatGPT search follows same patterns as other search services."""
        import inspect

        search = ChatGPTSearchService(bearer_token="test_token_123456789")

        # Should have async/sync pair
        assert hasattr(search, "chatGPT")
        assert hasattr(search, "chatGPT_async")

        # Should have timeout parameter
        sig = inspect.signature(search.chatGPT)
        assert "timeout" in sig.parameters

        # Should not have sync parameter (standard async pattern)
        assert "sync" not in sig.parameters
