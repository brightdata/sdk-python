import os
import re
import json
import openai
from typing import Dict, Any, Tuple, Union, List
from urllib.parse import urlparse

from ..utils import get_logger
from ..exceptions import ValidationError, APIError

logger = get_logger('api.extract')


class ExtractResult(str):
    """
    Custom result class that behaves like a string (extracted content) 
    but also provides access to metadata attributes
    """
    def __new__(cls, extracted_content, metadata):
        obj = str.__new__(cls, extracted_content)
        obj._metadata = metadata
        return obj
    
    def __getattr__(self, name):
        if name in self._metadata:
            return self._metadata[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __getitem__(self, key):
        return self._metadata[key]
    
    def get(self, key, default=None):
        return self._metadata.get(key, default)
    
    def keys(self):
        return self._metadata.keys()
    
    def values(self):
        return self._metadata.values()
    
    def items(self):
        return self._metadata.items()
    
    @property
    def metadata(self):
        """Access full metadata dictionary"""
        return self._metadata


class ExtractAPI:
    """Handles content extraction using web scraping + LLM processing"""
    
    def __init__(self, client):
        self.client = client
    
    def extract(self, query: str, url: Union[str, List[str]] = None, output_scheme: Dict[str, Any] = None, llm_key: str = None) -> Dict[str, Any]:
        """
        ## Extract specific information from websites using AI
        
        Combines web scraping with OpenAI's language models to extract targeted information
        from web pages based on natural language queries.
        
        ### Parameters:
        - `query` (str): Natural language query describing what to extract. If `url` parameter is provided,
                        this becomes the pure extraction query. If `url` is not provided, this should include 
                        the URL (e.g. "extract the most recent news from cnn.com")
        - `url` (str | List[str], optional): Direct URL(s) to scrape. If provided, bypasses URL extraction 
                        from query and sends these URLs to the web unlocker API
        - `output_scheme` (dict, optional): JSON Schema defining the expected structure for the LLM response.
                        Uses OpenAI's Structured Outputs for reliable type-safe responses.
                        Example: {"type": "object", "properties": {"title": {"type": "string"}, "date": {"type": "string"}}, "required": ["title", "date"]}
        - `llm_key` (str, optional): OpenAI API key. If not provided, uses OPENAI_API_KEY env variable
        
        ### Returns:
        - `ExtractResult`: String containing extracted content with metadata attributes access
        
        ### Example Usage:
        ```python
        # Using URL parameter with structured output
        result = client.extract(
            query="extract the most recent news headlines",
            url="https://cnn.com",
            output_scheme={
                "type": "object",
                "properties": {
                    "headlines": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "date": {"type": "string"}
                            },
                            "required": ["title", "date"]
                        }
                    }
                },
                "required": ["headlines"]
            }
        )
        
        # Using URL in query (original behavior)
        result = client.extract(
            query="extract the most recent news from cnn.com",
            llm_key="your-openai-api-key"
        )
        
        # Multiple URLs with structured schema
        result = client.extract(
            query="extract main headlines", 
            url=["https://cnn.com", "https://bbc.com"],
            output_scheme={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "source_name": {"type": "string"},
                                "headlines": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["source_name", "headlines"]
                        }
                    }
                },
                "required": ["sources"]
            }
        )
        ```
        
        ### Raises:
        - `ValidationError`: Invalid query format or missing LLM key
        - `APIError`: Scraping failed or LLM processing error
        """
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
        
        query = query.strip()
        if len(query) > 10000:
            raise ValidationError("Query is too long (maximum 10,000 characters)")
        if len(query) < 5:
            raise ValidationError("Query is too short (minimum 5 characters)")
        
        if not llm_key:
            llm_key = os.getenv('OPENAI_API_KEY')
        
        if not llm_key or not isinstance(llm_key, str):
            raise ValidationError("OpenAI API key is required. Provide it as parameter or set OPENAI_API_KEY environment variable")
        
        if output_scheme is not None:
            if not isinstance(output_scheme, dict):
                raise ValidationError("output_scheme must be a dict containing a valid JSON Schema")
            if "type" not in output_scheme:
                raise ValidationError("output_scheme must have a 'type' property")
            
            self._validate_structured_outputs_schema(output_scheme)
        
        logger.info(f"Processing extract query: {query[:50]}...")
        
        try:
            if url is not None:
                parsed_query = query.strip()
                target_urls = url if isinstance(url, list) else [url]
                logger.info(f"Using provided URL(s): {target_urls}")
            else:
                parsed_query, extracted_url = self._parse_query_and_url(query)
                target_urls = [extracted_url]
                logger.info(f"Parsed - Query: '{parsed_query}', URL: '{extracted_url}'")
            
            if len(target_urls) == 1:
                scraped_content = self.client.scrape(target_urls[0], response_format="raw")
                source_url = target_urls[0]
            else:
                scraped_content = self.client.scrape(target_urls, response_format="raw")
                source_url = ', '.join(target_urls)
            
            logger.info(f"Scraped content from {len(target_urls)} URL(s)")
            
            if isinstance(scraped_content, list):
                all_text = []
                all_titles = []
                for i, content in enumerate(scraped_content):
                    parsed = self.client.parse_content(
                        content, 
                        extract_text=True, 
                        extract_links=False, 
                        extract_images=False
                    )
                    all_text.append(f"--- Content from {target_urls[i]} ---\n{parsed.get('text', '')}")
                    all_titles.append(parsed.get('title', 'Unknown'))
                
                combined_text = "\n\n".join(all_text)
                combined_title = " | ".join(all_titles)
                parsed_content = {'text': combined_text, 'title': combined_title}
            else:
                parsed_content = self.client.parse_content(
                    scraped_content, 
                    extract_text=True, 
                    extract_links=False, 
                    extract_images=False
                )
                
            logger.info(f"Parsed content - text length: {len(parsed_content.get('text', ''))}")
            
            extracted_info, token_usage = self._process_with_llm(
                parsed_query, 
                parsed_content.get('text', ''), 
                llm_key,
                source_url,
                output_scheme
            )
            
            metadata = {
                'query': parsed_query,
                'url': source_url,
                'extracted_content': extracted_info,
                'source_title': parsed_content.get('title', 'Unknown'),
                'content_length': len(parsed_content.get('text', '')),
                'token_usage': token_usage,
                'success': True
            }
            
            return ExtractResult(extracted_info, metadata)
            
        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            logger.error(f"Unexpected error during extraction: {e}")
            raise APIError(f"Extraction failed: {str(e)}")
    
    def _parse_query_and_url(self, query: str) -> Tuple[str, str]:
        """
        Parse natural language query to extract the task and URL
        
        Args:
            query: Natural language query like "extract news from cnn.com"
            
        Returns:
            Tuple of (parsed_query, full_url)
        """
        query = query.strip()
        
        url_patterns = [
            r'from\s+((?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*)',
            r'on\s+((?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*)',
            r'at\s+((?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*)',
            r'((?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*)'
        ]
        
        url = None
        for pattern in url_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                url = match.group(1)
                break
        
        if not url:
            raise ValidationError("Could not extract URL from query. Please include a website URL.")
        
        full_url = self._build_full_url(url)
        
        extract_query = re.sub(r'\b(?:from|on|at)\s+(?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*', '', query, flags=re.IGNORECASE)
        extract_query = re.sub(r'\b(?:https?://)?(?:www\.)?[\w\.-]+(?:\.[\w]{2,})+(?:/[\w\.-]*)*', '', extract_query, flags=re.IGNORECASE)
        extract_query = re.sub(r'\s+', ' ', extract_query).strip()
        
        if not extract_query:
            extract_query = "extract the main content"
        
        return extract_query, full_url
    
    def _build_full_url(self, url: str) -> str:
        """
        Build a complete URL from potentially partial URL
        
        Args:
            url: Potentially partial URL like "cnn.com" or "https://example.com"
            
        Returns:
            Complete URL with https:// and www if needed
        """
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            if not url.startswith('www.'):
                url = f'www.{url}'
            url = f'https://{url}'
        
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValidationError(f"Invalid URL format: {url}")
        
        return url
    
    def _validate_structured_outputs_schema(self, schema: Dict[str, Any], path: str = "") -> None:
        """
        Validate JSON Schema for OpenAI Structured Outputs compatibility
        
        Args:
            schema: JSON Schema to validate
            path: Current path in schema (for error reporting)
        """
        if not isinstance(schema, dict):
            return
            
        schema_type = schema.get("type")
        
        if schema_type == "object":
            if "properties" not in schema:
                raise ValidationError(f"Object schema at '{path}' must have 'properties' defined")
            if "required" not in schema:
                raise ValidationError(f"Object schema at '{path}' must have 'required' array (OpenAI Structured Outputs requirement)")
            if "additionalProperties" not in schema or schema["additionalProperties"] is not False:
                raise ValidationError(f"Object schema at '{path}' must have 'additionalProperties': false (OpenAI Structured Outputs requirement)")
                
            properties = set(schema["properties"].keys())
            required = set(schema["required"])
            if properties != required:
                missing = properties - required
                extra = required - properties
                error_msg = f"OpenAI Structured Outputs requires ALL properties to be in 'required' array at '{path}'."
                if missing:
                    error_msg += f" Missing from required: {list(missing)}"
                if extra:
                    error_msg += f" Extra in required: {list(extra)}"
                raise ValidationError(error_msg)
                
            for prop_name, prop_schema in schema["properties"].items():
                self._validate_structured_outputs_schema(prop_schema, f"{path}.{prop_name}")
                
        elif schema_type == "array":
            if "items" in schema:
                self._validate_structured_outputs_schema(schema["items"], f"{path}[]")
    
    def _process_with_llm(self, query: str, content: str, llm_key: str, source_url: str, output_scheme: Dict[str, Any] = None) -> Tuple[str, Dict[str, int]]:
        """
        Process scraped content with OpenAI to extract requested information
        
        Args:
            query: What to extract from the content
            content: Scraped and parsed text content
            llm_key: OpenAI API key
            source_url: Source URL for context
            output_scheme: JSON Schema dict for structured outputs (optional)
            
        Returns:
            Tuple of (extracted information, token usage dict)
        """
        if len(content) > 15000:
            beginning = content[:8000]
            end = content[-4000:]
            content = f"{beginning}\n\n... [middle content truncated for token efficiency] ...\n\n{end}"
        elif len(content) > 12000:
            content = content[:12000] + "\n\n... [content truncated to optimize tokens]"
        
        client = openai.OpenAI(api_key=llm_key)
        
        system_prompt = f"""You are a precise web content extraction specialist. Your task: {query}

SOURCE: {source_url}

INSTRUCTIONS:
1. Extract ONLY the specific information requested
2. Include relevant details (dates, numbers, names) when available
3. If requested info isn't found, briefly state what content IS available
4. Keep response concise but complete
5. Be accurate and factual"""

        user_prompt = f"CONTENT TO ANALYZE:\n\n{content}\n\nEXTRACT: {query}"
        
        try:
            call_params = {
                "model": "gpt-4o-2024-08-06",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            if output_scheme:
                call_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extracted_content",
                        "strict": True,
                        "schema": output_scheme
                    }
                }
                logger.info("Using OpenAI Structured Outputs with provided schema")
            else:
                logger.info("Using regular OpenAI completion (no structured schema provided)")
            
            response = client.chat.completions.create(**call_params)
            
            if not response.choices or not response.choices[0].message.content:
                raise APIError("OpenAI returned empty response")
                
            extracted_content = response.choices[0].message.content.strip()
            
            if output_scheme:
                logger.info("Received structured JSON response from OpenAI")
            else:
                logger.info("Received text response from OpenAI")
            
            token_usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            logger.info(f"OpenAI token usage: {token_usage['total_tokens']} total ({token_usage['prompt_tokens']} prompt + {token_usage['completion_tokens']} completion)")
            
            return extracted_content, token_usage
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"Failed to process content with LLM: {str(e)}")