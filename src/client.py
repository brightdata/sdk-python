import os
import re
import time
import json
import requests
from .search import Search
from datetime import datetime
from .api.crawl import CrawlAPI
from .api.chatgpt import ChatGPTAPI
from .api.extract import ExtractAPI
from .api.download import DownloadAPI
from .api import WebScraper, SearchAPI
from typing import Union, Dict, Any, List
from .exceptions import ValidationError, AuthenticationError, APIError
from .api.linkedin import LinkedInAPI, LinkedInScraper, LinkedInSearcher
from .utils import ZoneManager, setup_logging, get_logger, parse_content

def _get_version():
    """Get version from __init__.py, cached at module import time."""
    try:
        init_file = os.path.join(os.path.dirname(__file__), '__init__.py')
        with open(init_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('"')[1]
    except (OSError, IndexError):
        pass
    return "unknown"

__version__ = _get_version()

logger = get_logger('client')


class bdclient:
    """Main client for the Bright Data SDK"""
    
    DEFAULT_MAX_WORKERS = 10
    DEFAULT_TIMEOUT = 30
    CONNECTION_POOL_SIZE = 20
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 1.5
    RETRY_STATUSES = {429, 500, 502, 503, 504}
    
    def __init__(
        self, 
        api_token: str = None,
        auto_create_zones: bool = True,
        web_unlocker_zone: str = None,
        serp_zone: str = None,
        browser_zone: str = None,
        browser_username: str = None,
        browser_password: str = None,
        browser_type: str = "playwright",
        log_level: str = "INFO",
        structured_logging: bool = True,
        verbose: bool = None
        ):
        """
        Initialize the Bright Data client with your API token.
    
        Create an account at https://brightdata.com/ to get your API token.
        Go to Settings > API Keys and verify that your key has "Admin" permissions.
    
        Args:
            api_token: Your Bright Data API token (or set BRIGHTDATA_API_TOKEN env var)
            auto_create_zones: Auto-create required zones if missing (default: True)
            web_unlocker_zone: Custom Web Unlocker zone name (default: 'sdk_unlocker')
            serp_zone: Custom SERP zone name (default: 'sdk_serp')
            browser_zone: Custom Browser zone name (default: 'sdk_browser')
            browser_username: Browser API username ("username-zone-{zone_name}")
            browser_password: Browser API password
            browser_type: "playwright", "puppeteer", or "selenium" (default: "playwright")
            log_level: Logging level
            structured_logging: Enable structured JSON logging
            verbose: When True, show all logs per log_level. Can also use BRIGHTDATA_VERBOSE env var.
        """

        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
    
        if verbose is None:
            env_verbose = os.getenv('BRIGHTDATA_VERBOSE', '').lower()
            verbose = env_verbose in ('true', '1', 'yes', 'on')
    
        setup_logging(log_level, structured_logging, verbose)
        logger.info("Initializing Bright Data SDK client")
    
        # API Token Validation
        self.api_token = api_token or os.getenv('BRIGHTDATA_API_TOKEN')
        if not self.api_token:
            logger.error("API token not provided")
            raise ValidationError(
                "API token is required. Pass api_token or set BRIGHTDATA_API_TOKEN env var."
            )
    
        if not isinstance(self.api_token, str):
            logger.error("API token must be a string")
            raise ValidationError("API token must be a string")
    
        if len(self.api_token.strip()) < 10:
            logger.error("API token appears to be invalid (too short)")
            raise ValidationError("API token appears to be invalid")
    
        token_preview = f"{self.api_token[:4]}***{self.api_token[-4:]}"
        logger.info(f"API token validated successfully: {token_preview}")
    
        self.web_unlocker_zone = web_unlocker_zone or os.getenv('WEB_UNLOCKER_ZONE', 'sdk_unlocker')
        self.serp_zone = serp_zone or os.getenv('SERP_ZONE', 'sdk_serp')
        self.browser_zone = browser_zone or os.getenv('BROWSER_ZONE', 'sdk_browser')
        self.auto_create_zones = auto_create_zones
    
        self.browser_username = browser_username or os.getenv('BRIGHTDATA_BROWSER_USERNAME')
        self.browser_password = browser_password or os.getenv('BRIGHTDATA_BROWSER_PASSWORD')
    
        valid_browser_types = ["playwright", "puppeteer", "selenium"]
        if browser_type not in valid_browser_types:
            raise ValidationError(
                f"Invalid browser_type '{browser_type}'. Must be one of: {valid_browser_types}"
            )
        self.browser_type = browser_type
    
        if self.browser_username and self.browser_password:
            browser_preview = f"{self.browser_username[:3]}***"
            logger.info(f"Browser credentials configured: {browser_preview} (type: {self.browser_type})")
        elif self.browser_username or self.browser_password:
            logger.warning("Incomplete browser credentials: both username and password are required.")
        else:
            logger.debug("No browser credentials provided - browser API will not be available.")
    
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': f'brightdata-sdk/{__version__}'
        })
        logger.info("HTTP session configured with secure headers")
    
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=self.CONNECTION_POOL_SIZE,
            pool_maxsize=self.CONNECTION_POOL_SIZE,
            max_retries=0
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
    
        self.zone_manager = ZoneManager(self.session)
    
        self.web_scraper = WebScraper(
            self.session,
            self.DEFAULT_TIMEOUT,
            self.MAX_RETRIES,
            self.RETRY_BACKOFF_FACTOR
        )
    
        self.search_api = SearchAPI(
            self.session,
            self.DEFAULT_TIMEOUT,
            self.MAX_RETRIES,
            self.RETRY_BACKOFF_FACTOR
        )
    
        self.chatgpt_api = ChatGPTAPI(
            self.session,
            self.api_token,
            self.DEFAULT_TIMEOUT,
            self.MAX_RETRIES,
            self.RETRY_BACKOFF_FACTOR
        )
    
        self.linkedin_api = LinkedInAPI(
            self.session,
            self.api_token,
            self.DEFAULT_TIMEOUT,
            self.MAX_RETRIES,
            self.RETRY_BACKOFF_FACTOR
        )
    
        self.download_api = DownloadAPI(self.session, self.api_token, self.DEFAULT_TIMEOUT)
    
        self.crawl_api = CrawlAPI(
            self.session,
            self.api_token,
            self.DEFAULT_TIMEOUT,
            self.MAX_RETRIES,
            self.RETRY_BACKOFF_FACTOR
        )
    
        self.extract_api = ExtractAPI(self)
    
        self.search = Search(self)
    
        if self.auto_create_zones:
            self.zone_manager.ensure_required_zones(
                self.web_unlocker_zone,
                self.serp_zone
            )

    
    def scrape(
        self,
        url: Union[str, List[str]],
        zone: str = None,
        response_format: str = "raw",
        method: str = "GET", 
        country: str = "",
        data_format: str = "html",
        async_request: bool = False,
        max_workers: int = None,
        timeout: int = None
    ) -> Union[Dict[str, Any], str, List[Union[Dict[str, Any], str]]]:
        """
        ## Unlock and scrape websites using Bright Data Web Unlocker API
        
        Scrapes one or multiple websites using Bright Data's Web Unlocker and proxy network.
        Automatically handles bot-detection, CAPTCHAs, and retries.
        
        ### Parameters:
        - `url` (str | List[str]): Single URL string or list of URLs to scrape
        - `zone` (str, optional): Zone identifier (default: auto-configured web_unlocker_zone)
        - `response_format` (str, optional): Response format - `"json"` for structured data, `"raw"` for HTML string (default: `"raw"`)
        - `method` (str, optional): HTTP method for the request (default: `"GET"`)
        - `country` (str, optional): Two-letter ISO country code for proxy location (defaults to fastest connection)
        - `data_format` (str, optional): Additional format transformation (default: `"html"`)
        - `async_request` (bool, optional): Enable asynchronous processing (default: `False`)
        - `max_workers` (int, optional): Maximum parallel workers for multiple URLs (default: `10`)
        - `timeout` (int, optional): Request timeout in seconds (default: `30`)
        
        ### Returns:
        - Single URL: `Dict[str, Any]` if `response_format="json"`, `str` if `response_format="raw"`
        - Multiple URLs: `List[Union[Dict[str, Any], str]]` corresponding to each input URL
        
        ### Raises:
        - `ValidationError`: Invalid URL or parameters
        - `APIError`: Scraping failed (non-2xx response or server error)
        """
        
        # URL validation
        
        if not url:
            raise ValidationError("The 'url' parameter cannot be None or empty.")

        if isinstance(url, str):
            if not url.strip():
                raise ValidationError("The 'url' string cannot be empty or whitespace.")
        elif isinstance(url, list):
            if len(url) == 0:
                raise ValidationError("URL list cannot be empty")
            if any((not isinstance(u, str) or not u.strip()) for u in url):
                raise ValidationError("All URLs in the list must be non-empty strings")
        
        result = self.web_scraper.scrape(
            url, zone or self.web_unlocker_zone, response_format, method, country,
            data_format, async_request, max_workers or self.DEFAULT_MAX_WORKERS, timeout or self.DEFAULT_TIMEOUT
        )
        return result

    def search(
        self,
        query: Union[str, List[str]],
        search_engine: str = "google",
        zone: str = None,
        response_format: str = "raw",
        method: str = "GET",
        country: str = "",
        data_format: str = "html",
        async_request: bool = False,
        max_workers: int = None,
        timeout: int = None,
        parse: bool = False
    ) -> Union[Dict[str, Any], str, List[Union[Dict[str, Any], str]]]:
        """
        ## Perform web search using Bright Data's SERP
        
        ### Parameters:
        - `query` (str | List[str]): Search query string or list of search queries
        - `search_engine` (str, optional): Search engine to use - `"google"`, `"bing"`, or `"yandex"` (default: `"google"`)
        - `zone` (str, optional): Zone identifier (default: auto-configured serp_zone)
        - `response_format` (str, optional): Response format - `"json"` for structured data, `"raw"` for HTML string (default: `"raw"`)
        - `method` (str, optional): HTTP method for the request (default: `"GET"`)
        - `country` (str, optional): Two-letter ISO country code for proxy location (default: `"us"`)
        - `data_format` (str, optional): Additional format transformation (default: `"html"`)
        - `async_request` (bool, optional): Enable asynchronous processing (default: `False`)
        - `max_workers` (int, optional): Maximum parallel workers for multiple queries (default: `10`)
        - `timeout` (int, optional): Request timeout in seconds (default: `30`)
        - `parse` (bool, optional): Enable JSON parsing by adding brd_json=1 to URL (default: `False`)
        
        ### Returns:
        - Single query: `Dict[str, Any]` if `response_format="json"`, `str` if `response_format="raw"`
        - Multiple queries: `List[Union[Dict[str, Any], str]]` corresponding to each input query
        
        ### Raises:
        - `ValidationError`: Query is missing or invalid
        - `APIError`: Search request failed or returned an error
        """
        
        # Query validation
        
        if not query:
            raise ValidationError("query cannot be empty")
        if isinstance(query, str):
            if not query.strip():
                raise ValidationError("Search query cannot be empty or whitespace")
        elif isinstance(query, list):
            if len(query) == 0:
                raise ValidationError("Query list cannot be empty")
            for q in query:
                if not isinstance(q, str) or not q.strip():
                    raise ValidationError("All queries in the list must be non-empty strings")
                    
        # Validate search engine
        
        search_engine = (search_engine or "google").strip().lower()
        valid_engines = ["google", "bing", "yandex"]
        if search_engine not in valid_engines:
            raise ValidationError(f"Invalid search engine '{search_engine}'. Valid options: {', '.join(valid_engines)}")

        zone = zone or self.serp_zone
        max_workers = max_workers or self.DEFAULT_MAX_WORKERS
        
        result = self.search_api.search(
        query=query,
        search_engine=search_engine,
        zone=zone or self.serp_zone,
        response_format=response_format,
        method=method,
        country=country,
        data_format=data_format,
        async_request=async_request,
        max_workers=max_workers,
        timeout=timeout or self.DEFAULT_TIMEOUT,
        parse=parse,
        )

        return result

    def download_content(self, content: Union[Dict, str], filename: str = None, format: str = "json", parse: bool = False) -> str:
        """
        ## Download content to a file based on its format
        
        ### Args:
            content: The content to download (dict for JSON, string for other formats)
            filename: Optional filename. If not provided, generates one with timestamp
            format: Format of the content ("json", "csv", "ndjson", "jsonl", "txt")
            parse: If True, automatically parse JSON strings in 'body' fields to objects (default: False)
        
        ### Returns:
            The file path of the saved file.
        """
        if not content:
            raise ValidationError("Content is empty or None")
        return self.download_api.download_content(content, filename, response_format, parse)
    

    def search_gpt(
        self,
        prompt: Union[str, List[str]],
        country: Union[str, List[str]] = None,
        additional_prompt: Union[str, List[str]] = None,
        web_search: Union[bool, List[bool]] = False,
        sync: bool = True,
        timeout: int = None,
        **kwargs
    ) -> Dict[str, Any]:

        """
        ## Search ChatGPT responses using Bright Data's ChatGPT dataset API
        
        Sends one or multiple prompts to ChatGPT through Bright Data's proxy network 
        with support for both synchronous and asynchronous processing.
        
        ### Parameters:
        - `prompt` (str | List[str]): Single prompt string or list of prompts to send to ChatGPT
        - `country` (str | List[str], optional): Two-letter ISO country code(s) for proxy location (default: "")
        - `additional_prompt` (str | List[str], optional): Follow-up prompt(s) after receiving the first answer (default: "")
        - `web_search` (bool | List[bool], optional): Whether to click the web search button in ChatGPT (default: False)
        - `sync` (bool, optional): If True (default), returns data immediately. If False, returns snapshot_id for async processing
        
        ### Returns:
        - `Dict[str, Any]`: If sync=True, returns ChatGPT response data directly. If sync=False, returns response with snapshot_id for async processing
        
        ### Raises:
        - `ValidationError`: Invalid prompt or parameters
        - `AuthenticationError`: Invalid API token or insufficient permissions
        - `APIError`: Request failed or server error
        """
        
       # Handle alternate parameter names from kwargs
        
        if 'secondaryPrompt' in kwargs:
            additional_prompt = kwargs.pop('secondaryPrompt')
        if 'additionalPrompt' in kwargs:
            additional_prompt = kwargs.pop('additionalPrompt')
        if 'webSearch' in kwargs:
            web_search = kwargs.pop('webSearch')
            
        # Validate prompt input
        
        if (isinstance(prompt, list) and len(prompt) == 0) or prompt is None:
            raise ValidationError("prompt is required")
            
        # Ensure prompts list
        
        prompts = prompt if isinstance(prompt, list) else [prompt]
        
        # Validate each prompt is a non-empty string
        
        for p in prompts:
            if not isinstance(p, str) or not p.strip():
                raise ValidationError("All prompts must be non-empty strings")
        
        def normalize_param(param, name):
            if param is None:
                return [None] * len(prompts)
            if isinstance(param, list):
                if len(param) != len(prompts):
                    raise ValidationError(f"Length of {name} list must match number of prompts")
                return param
            return [param] * len(prompts)
        
        countries = normalize_param(country, "country")
        followups = normalize_param(additional_prompt, "additional_prompt")
        web_searches = normalize_param(web_search, "web_search")
        
         # Validate country codes
        for i, c in enumerate(countries):
            if c is None or str(c).strip() == "":
                countries[i] = ""
            else:
                if not isinstance(c, str) or len(c.strip()) != 2 or not c.strip().isalpha():
                    raise ValidationError("must be 2-letter code")
                countries[i] = c.strip().lower()
        # Validate follow-up prompts
        for i, f in enumerate(followups):
            if f is None:
                followups[i] = ""
            elif not isinstance(f, str):
                raise ValidationError("All follow-up prompts must be strings")
            else:
                followups[i] = f.strip()
        # Validate web_search flags
        for i, w in enumerate(web_searches):
            if w is None:
                web_searches[i] = False
            elif not isinstance(w, bool):
                raise ValidationError("must be a boolean or list of booleans")
    
        timeout_value = timeout if timeout is not None else (65 if sync else 30)
        
        if timeout is not None:
            if not isinstance(timeout, int):
                raise ValidationError("Timeout must be an integer")
            if timeout <= 0:
                raise ValidationError("Timeout must be greater than 0 seconds")
            if timeout > 300:
                raise ValidationError("Timeout cannot exceed 300 seconds (5 minutes)")
        # Prepare request payload
        tasks = []
        for i in range(len(prompts)):
            task = {
                "url": "https://chatgpt.com",
                "prompt": prompts[i].strip(),
                "country": countries[i] or "",
                "additional_prompt": followups[i] or "",
                "web_search": bool(web_searches[i])
            }
            tasks.append(task)
        payload_data = tasks[0] if len(tasks) == 1 else tasks
        # Make API request with retries
        endpoint = "https://api.brightdata.com/datasets/v3/scrape" if sync else "https://api.brightdata.com/datasets/v3/trigger"
        params = {
            "dataset_id": "gd_m7aof0k82r803d5bjm",
            "include_errors": "true"
        }
        last_exception = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self.session.post(endpoint, json=payload_data, timeout=timeout_value)
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt >= self.MAX_RETRIES:
                    raise NetworkError(f"Network error: {e}")
                # Retry on network errors
                time.sleep(self.RETRY_BACKOFF_FACTOR ** attempt)
                continue
            if response.status_code == 401:
                raise AuthenticationError("Invalid API token or unauthorized")
            if response.status_code in self.RETRY_STATUSES:
                if attempt >= self.MAX_RETRIES:
                    raise RuntimeError("Failed after retries")
                time.sleep(self.RETRY_BACKOFF_FACTOR ** attempt)
                continue
            if response.status_code != 200:
                raise APIError(f"ChatGPT search failed with status {response.status_code}: {response.text}", status_code=response.status_code, response_text=getattr(response, 'text', ''))
            # Success
            result_data = response.json()
            if sync:
                return result_data
            snapshot_id = result_data.get("snapshot_id") or result_data.get("id")
            if snapshot_id:
                print(f"Snapshot ID: {snapshot_id}")
                return {"snapshot_id": snapshot_id}
            else:
                raise APIError("Failed to retrieve snapshot ID from response", status_code=response.status_code, response_text=response.text)
 

    @property
    def scrape_linkedin(self):
        """
        ## LinkedIn Data Scraping Interface
        
        Provides specialized methods for scraping different types of LinkedIn data
        using Bright Data's collect API with pre-configured dataset IDs.
        
        ### Available Methods:
        - `profiles(url)` - Scrape LinkedIn profile data
        - `companies(url)` - Scrape LinkedIn company data  
        - `jobs(url)` - Scrape LinkedIn job listing data
        - `posts(url)` - Scrape LinkedIn post content
        
        ### Example Usage:
        ```python
        # Scrape LinkedIn profiles
        result = client.scrape_linkedin.profiles("https://www.linkedin.com/in/username/")
        
        # Scrape multiple companies
        companies = [
            "https://www.linkedin.com/company/ibm",
            "https://www.linkedin.com/company/bright-data"
        ]
        result = client.scrape_linkedin.companies(companies)
        
        # Scrape job listings
        result = client.scrape_linkedin.jobs("https://www.linkedin.com/jobs/view/123456/")
        
        # Scrape posts
        result = client.scrape_linkedin.posts("https://www.linkedin.com/posts/user-activity-123/")
        ```
        
        ### Returns:
        Each method returns a `Dict[str, Any]` containing snapshot_id and metadata for tracking the request.
        Use the snapshot_id with `download_snapshot()` to retrieve the collected data.
        """
        if not hasattr(self, '_linkedin_scraper'):
            self._linkedin_scraper = LinkedInScraper(self.linkedin_api)
        return self._linkedin_scraper

    @property
    def search_linkedin(self):
        """
        ## LinkedIn Data Search Interface
        
        Provides specialized methods for discovering new LinkedIn data by various search criteria
        using Bright Data's collect API with pre-configured dataset IDs.
        
        ### Available Methods:
        - `profiles(first_name, last_name)` - Search LinkedIn profiles by name
        - `jobs(url=..., location=...)` - Search LinkedIn jobs by URL or keyword criteria
        - `posts(profile_url=..., company_url=..., url=...)` - Search LinkedIn posts by various methods
        
        ### Example Usage:
        ```python
        # Search profiles by name
        result = client.search_linkedin.profiles("James", "Smith")
        
        # Search jobs by location and keywords
        result = client.search_linkedin.jobs(
            location="Paris", 
            keyword="product manager", 
            country="FR"
        )
        
        # Search posts by profile URL with date range
        result = client.search_linkedin.posts(
            profile_url="https://www.linkedin.com/in/username",
            start_date="2018-04-25T00:00:00.000Z",
            end_date="2021-05-25T00:00:00.000Z"
        )
        ```
        
        ### Returns:
        Each method returns a `Dict[str, Any]` containing snapshot_id (async) or direct data (sync) for tracking the request.
        Use the snapshot_id with `download_snapshot()` to retrieve the collected data.
        """
        if not hasattr(self, '_linkedin_searcher'):
            self._linkedin_searcher = LinkedInSearcher(self.linkedin_api)
        return self._linkedin_searcher

    def download_snapshot(
        self,
        snapshot_id: str,
        response_format: str = "json",
        compress: bool = False,
        batch_size: int = None,
        part: int = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        """
        ## Download snapshot content from Bright Data dataset API
        
        Downloads the snapshot content using the snapshot ID returned from scrape_chatGPT() 
        or other dataset collection triggers.
        
        ### Parameters:
        - `snapshot_id` (str): The snapshot ID returned when collection was triggered (required)
        - `response_format` (str, optional): Format of the output data: "json", "csv", "ndjson", "jsonl" (default: "json")
        - `compress` (bool, optional): Whether the result should be compressed (default: False)
        - `batch_size` (int, optional): Divide into batches of X records (minimum: 1000)
        - `part` (int, optional): If batch_size provided, specify which part to download
        
        ### Returns:
        - `Union[Dict, List, str]`: Snapshot data in the requested format, OR
        - `Dict`: Status response if snapshot is not ready yet (status="not_ready")
        
       
        ### Raises:
        - `ValidationError`: Invalid parameters or snapshot_id format
        - `APIError`: Request failed, snapshot not found, or server error
        """
        
        # snapshot_id validation
    
        if not snapshot_id or not isinstance(snapshot_id, str):
            raise ValidationError("The 'snapshot_id' parameter must be a non-empty string.")
        if not snapshot_id.startswith("s_"):
            raise ValidationError("Invalid 'snapshot_id' format. Expected an ID starting with 's_' (e.g., 's_m4x7enmven8djfqak').")
        
        # format validation
    
        allowed_formats = {"json", "ndjson", "jsonl", "csv"}
        if format not in allowed_formats:
            raise ValueError(
                f"Invalid 'format' value: '{format}'. Must be one of {sorted(allowed_formats)}."
            )

        return self.download_api.download_snapshot(snapshot_id, response_format, compress, batch_size, part)


    def list_zones(self) -> List[Dict[str, Any]]:
        """
        ## List all active zones in your Bright Data account
        
        ### Returns:
            List of zone dictionaries with their configurations
        """
        return self.zone_manager.list_zones()

    def connect_browser(self) -> str:
        """
        ## Get WebSocket endpoint URL for connecting to Bright Data's scraping browser
        
        Returns the WebSocket endpoint URL that can be used with Playwright or Selenium
        to connect to Bright Data's scraping browser service.

        **Security Warning:** The returned URL contains authentication credentials. Do not share this URL or expose it publicly.

        ### Returns:
            WebSocket URL (str) for connecting to the browser (contains one-time token)
        
        ### Raises:
            - `AuthenticationError`: If the API token or browser zone credentials are invalid
            - `APIError`: If retrieving the browser endpoint fails
        """
        
        if not self.browser_username or not self.browser_password:
            logger.error("Browser credentials not configured")
            raise ValidationError(
                "Browser credentials are required. Provide browser_username and browser_password "
                "parameters or set BRIGHTDATA_BROWSER_USERNAME and BRIGHTDATA_BROWSER_PASSWORD "
                "environment variables."
            )
        
        if not isinstance(self.browser_username, str) or not isinstance(self.browser_password, str):
            logger.error("Browser credentials must be strings")
            raise ValidationError("Browser username and password must be strings")
        
        if len(self.browser_username.strip()) == 0 or len(self.browser_password.strip()) == 0:
            logger.error("Browser credentials cannot be empty")
            raise ValidationError("Browser username and password cannot be empty")
        
        auth_string = f"{self.browser_username}:{self.browser_password}"
        
        if self.browser_type == "selenium":
            endpoint_url = f"https://{auth_string}@brd.superproxy.io:9515"
            logger.debug(f"Browser endpoint URL: https://***:***@brd.superproxy.io:9515")
        else:
            endpoint_url = f"wss://{auth_string}@brd.superproxy.io:9222"
            logger.debug(f"Browser endpoint URL: wss://***:***@brd.superproxy.io:9222")
        
        logger.info(f"Generated {self.browser_type} connection endpoint for user: {self.browser_username[:3]}***")
        
        return endpoint_url

    def crawl(
        self,
        url: Union[str, List[str]],
        ignore_sitemap: bool = None,
        depth: int = None,
        include_filter: str = None,
        exclude_filter: str = None,
        custom_output_fields: List[str] = None,
        include_errors: bool = True
    ) -> Dict[str, Any]:
        """
        ## Crawl websites using Bright Data's Web Crawl API
        
        Performs web crawling to discover and scrape multiple pages from a website
        starting from the specified URL(s). Returns a snapshot_id for tracking the crawl progress.
        
        ### Parameters:
            - `url` (str | List[str]): Starting URL or URLs to crawl
            - `ignore_sitemap` (bool, optional): If True, ignore site's sitemap (default: False)
            - `depth` (int, optional): Maximum crawl depth (number of hops from start URL)
            - `include_filter` (str, optional): Only crawl URLs that include this substring (default: None)
            - `exclude_filter` (str, optional): Do not crawl URLs that include this substring
            - `custom_output_fields` (List[str], optional): Additional data fields to return (e.g., ["markdown","text","title"])
            - `include_errors` (bool, optional): If True, include pages that errored in results (default: True)
        
        ### Returns:
            - A dict containing the crawl job details, including a `snapshot_id` to retrieve results via download_snapshot()
        
        ### Raises:
            - `ValidationError`: Missing URL or invalid parameters
            - `APIError`: Crawl request failed
        """

        # URL validation
        
        if not url:
            raise ValidationError("The 'url' parameter cannot be None or empty.")
        if isinstance(url, str):
            if not url.strip():
                raise ValidationError("The 'url' string cannot be empty or whitespace.")
        elif isinstance(url, list):
            if len(url) == 0:
                raise ValidationError("URL list cannot be empty")
            for u in url:
                if not isinstance(u, str) or not u.strip():
                    raise ValidationError("All URLs in the list must be non-empty strings")
        if depth is not None:
            if not isinstance(depth, int):
                raise ValidationError("Depth must be an integer")
            if depth <= 0:
                raise ValidationError("The 'depth' parameter must be a positive integer.")
        
        result = self.crawl_api.crawl(
            url, ignore_sitemap, depth, include_filter, exclude_filter, custom_output_fields, include_errors
        )
        return result

    def parse_content(
        self,
        data: Union[str, Dict, List],
        extract_text: bool = True,
        extract_links: bool = False,
        extract_images: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        ## Parse content from API responses
        
        Extract and parse useful information from scraping, search, or crawling results.
        Automatically detects and handles both single and multiple results from batch operations.
        
        ### Parameters:
        - `data` (str | Dict | List): Response data from scrape(), search(), or crawl() methods
        - `extract_text` (bool, optional): Extract clean text content (default: True)
        - `extract_links` (bool, optional): Extract all links from content (default: False)
        - `extract_images` (bool, optional): Extract image URLs from content (default: False)
        
        ### Returns:
        - `Dict[str, Any]`: Parsed content for single results
        - `List[Dict[str, Any]]`: List of parsed content for multiple results (auto-detected)
        """
        
        return parse_content(
            data=data,
            extract_text=extract_text,
            extract_links=extract_links,
            extract_images=extract_images
        )

    def extract(self, query: str, url: Union[str, List[str]] = None, output_scheme: Dict[str, Any] = None, llm_key: str = None) -> str:
        """
        ## Extract specific information from websites using AI
        
        Combines web scraping with OpenAI's language models to extract targeted information
        from web pages based on natural language queries. Automatically parses URLs and
        optimizes content for efficient LLM processing.

        **LLM Key Notice:** If `llm_key` is not provided, the method will attempt to read 
        the OpenAI API key from the `OPENAI_API_KEY` environment variable. Ensure it is set.

        ### Parameters:
        - `query` (str): Natural language query describing what to extract. If `url` parameter is provided,
                         the extraction will run on that URL. Otherwise, a prior scrape result should be provided.
        - `url` (str | List[str], optional): Target page URL(s) to extract information from. Can be omitted if using a prior result.
        - `output_scheme` (Dict, optional): JSON schema defining the structure of desired output (keys and value types)
        - `llm_key` (str, optional): OpenAI API key for LLM usage (if not provided, will use environment variable)

        ### Returns:
        - `str`: The extracted information as a text string (may contain JSON or markdown depending on query and output_scheme)
        
        ### Raises:
        - `ValidationError`: Missing query, missing URL, or invalid LLM key
        """

        # Validate LLM key
        if not llm_key:
            raise ValidationError(
                "Missing API key. Provide it via the `llm_key` parameter or set the "
                "`BRIGHTDATA_API_TOKEN` environment variable. Example:\n\n"
                "export BRIGHTDATA_API_TOKEN='your-openai-api-key'"
            )
            
        return self.extract_api.extract(query, url, output_scheme, llm_key)
