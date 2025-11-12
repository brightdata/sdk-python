"""
SERP (Search Engine Results Page) API service.

Philosophy:
- SERP data normalized across engines for easy comparison
- Search engine quirks handled transparently
- Results include ranking position and competitive context
- Consistent interface regardless of search engine
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone
from urllib.parse import quote_plus

from .base import BaseAPI
from ..models import SearchResult
from ..types import NormalizedSERPData, URLParam, OptionalURLParam
from ..exceptions import ValidationError, APIError
from ..utils.validation import validate_zone_name, validate_country_code


class BaseSERPService(BaseAPI):
    """
    Base class for SERP (Search Engine Results Page) services.
    
    Provides common patterns for search result extraction across
    different search engines (Google, Bing, Yandex, etc.).
    
    All SERP services share:
    - Normalized result format (SearchResult)
    - Location and language targeting
    - Ranking position tracking
    - Organic results, ads, and SERP features
    """
    
    SEARCH_ENGINE: str = ""  # Override in subclasses
    ENDPOINT = "/request"
    
    async def _execute_async(self, *args: Any, **kwargs: Any) -> Any:
        """Execute API operation asynchronously."""
        return await self.search_async(*args, **kwargs)
    
    async def search_async(
        self,
        query: Union[str, List[str]],
        zone: str,
        location: Optional[str] = None,
        language: str = "en",
        device: str = "desktop",
        num_results: int = 10,
        **kwargs
    ) -> Union[SearchResult, List[SearchResult]]:
        """
        Perform search asynchronously.
        
        Args:
            query: Search query string or list of queries
            zone: Bright Data zone for SERP API
            location: Geographic location (country, city, or coordinates)
            language: Language code (e.g., "en", "es", "fr")
            device: Device type ("desktop", "mobile", "tablet")
            num_results: Number of results to return
            **kwargs: Engine-specific parameters
        
        Returns:
            SearchResult for single query, List[SearchResult] for multiple
        
        Raises:
            ValidationError: Invalid input parameters
            APIError: Search request failed
        """
        # Normalize to list for processing
        is_single = isinstance(query, str)
        query_list = [query] if is_single else query
        
        # Validate
        validate_zone_name(zone)
        self._validate_queries(query_list)
        
        # Process queries
        if len(query_list) == 1:
            return await self._search_single_async(
                query=query_list[0],
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                **kwargs
            )
        else:
            return await self._search_multiple_async(
                queries=query_list,
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                **kwargs
            )
    
    def search(self, *args, **kwargs):
        """Synchronous search wrapper."""
        return self._execute_sync(*args, **kwargs)
    
    async def _search_single_async(
        self,
        query: str,
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> SearchResult:
        """Execute single search query."""
        request_sent_at = datetime.now(timezone.utc)
        
        # Build search URL based on engine
        search_url = self._build_search_url(
            query=query,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
            **kwargs
        )
        
        # Build request payload
        payload = {
            "zone": zone,
            "url": search_url,
            "format": "json",  # Always request JSON for SERP
            "method": "GET",
        }
        
        try:
            # Make request
            async with self.engine._session.post(
                f"{self.engine.BASE_URL}{self.ENDPOINT}",
                json=payload,
                headers=self.engine._session.headers
            ) as response:
                data_received_at = datetime.now(timezone.utc)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Normalize SERP data
                    normalized_data = self.normalize_serp_data(data)
                    
                    return SearchResult(
                        success=True,
                        query={"q": query, "location": location, "language": language},
                        data=normalized_data.get("results", []),
                        total_found=normalized_data.get("total_results"),
                        search_engine=self.SEARCH_ENGINE,
                        country=location,
                        results_per_page=num_results,
                        request_sent_at=request_sent_at,
                        data_received_at=data_received_at,
                    )
                else:
                    error_text = await response.text()
                    return SearchResult(
                        success=False,
                        query={"q": query},
                        error=f"Search failed (HTTP {response.status}): {error_text}",
                        search_engine=self.SEARCH_ENGINE,
                        request_sent_at=request_sent_at,
                        data_received_at=data_received_at,
                    )
        
        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            
            return SearchResult(
                success=False,
                query={"q": query},
                error=f"Unexpected error: {str(e)}",
                search_engine=self.SEARCH_ENGINE,
                request_sent_at=datetime.now(timezone.utc),
                data_received_at=datetime.now(timezone.utc),
            )
    
    async def _search_multiple_async(
        self,
        queries: List[str],
        zone: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> List[SearchResult]:
        """Execute multiple search queries concurrently."""
        tasks = [
            self._search_single_async(
                query=q,
                zone=zone,
                location=location,
                language=language,
                device=device,
                num_results=num_results,
                **kwargs
            )
            for q in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    SearchResult(
                        success=False,
                        query={"q": queries[i]},
                        error=f"Exception: {str(result)}",
                        search_engine=self.SEARCH_ENGINE,
                        request_sent_at=datetime.now(timezone.utc),
                        data_received_at=datetime.now(timezone.utc),
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _validate_queries(self, queries: List[str]) -> None:
        """Validate search queries."""
        if not queries:
            raise ValidationError("Query list cannot be empty")
        
        for query in queries:
            if not query or not isinstance(query, str):
                raise ValidationError(f"Invalid query: {query}. Must be non-empty string.")
    
    def _build_search_url(
        self,
        query: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> str:
        """
        Build search URL for engine.
        
        Override in subclasses to build engine-specific URLs.
        """
        raise NotImplementedError("Subclasses must implement _build_search_url")
    
    def normalize_serp_data(self, data: Any) -> NormalizedSERPData:
        """
        Normalize SERP data to consistent format.
        
        Override in subclasses to handle engine-specific response formats.
        
        Returns normalized dict with:
        - results: List of search results
        - total_results: Total available results
        - featured_snippet: Featured snippet if present
        - knowledge_panel: Knowledge panel if present
        - ads: Sponsored results if present
        """
        # Base implementation returns data as-is
        if isinstance(data, dict):
            return data
        
        return {"results": data if isinstance(data, list) else []}


class GoogleSERPService(BaseSERPService):
    """
    Google Search Engine Results Page service.
    
    Provides normalized Google search results including:
    - Organic search results with ranking positions
    - Featured snippets
    - Knowledge panels
    - People Also Ask
    - Related searches
    - Sponsored/ad results
    
    Example:
        >>> async with AsyncEngine(token) as engine:
        ...     service = GoogleSERPService(engine)
        ...     result = await service.search_async(
        ...         query="python tutorial",
        ...         zone="serp_zone",
        ...         location="United States",
        ...         language="en"
        ...     )
        ...     for item in result.data:
        ...         print(item['title'], item['url'])
    """
    
    SEARCH_ENGINE = "google"
    
    def _build_search_url(
        self,
        query: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> str:
        """
        Build Google search URL with parameters.
        
        Args:
            query: Search query
            location: Location (country name or code)
            language: Language code
            device: Device type
            num_results: Number of results
            **kwargs: Additional Google-specific params
        
        Returns:
            Google search URL with encoded parameters
        """
        encoded_query = quote_plus(query)
        
        # Base Google search URL
        url = f"https://www.google.com/search?q={encoded_query}"
        
        # Add number of results
        url += f"&num={num_results}"
        
        # Add language
        if language:
            url += f"&hl={language}"
        
        # Add location (Google uses gl parameter for country)
        if location:
            # Convert location to country code if needed
            location_code = self._parse_location_to_code(location)
            if location_code:
                url += f"&gl={location_code}"
        
        # Device-specific parameters
        if device == "mobile":
            url += "&mobileaction=1"
        
        # Additional parameters
        if "safe_search" in kwargs:
            url += f"&safe={'active' if kwargs['safe_search'] else 'off'}"
        
        if "time_range" in kwargs:
            # qdr parameter: h=hour, d=day, w=week, m=month, y=year
            url += f"&tbs=qdr:{kwargs['time_range']}"
        
        return url
    
    def _parse_location_to_code(self, location: str) -> str:
        """
        Parse location string to country code.
        
        Args:
            location: Location name or code
        
        Returns:
            Two-letter country code
        """
        # Common location mappings
        location_map = {
            "united states": "us",
            "usa": "us",
            "united kingdom": "gb",
            "uk": "gb",
            "canada": "ca",
            "australia": "au",
            "germany": "de",
            "france": "fr",
            "spain": "es",
            "italy": "it",
            "japan": "jp",
            "china": "cn",
            "india": "in",
            "brazil": "br",
        }
        
        location_lower = location.lower().strip()
        
        # Check if already a country code (2 letters)
        if len(location_lower) == 2:
            return location_lower.upper()
        
        # Look up in mapping
        return location_map.get(location_lower, "us")  # Default to US
    
    def normalize_serp_data(self, data: Any) -> NormalizedSERPData:
        """
        Normalize Google SERP data to consistent format.
        
        Extracts and structures:
        - Organic results with positions
        - Featured snippets
        - Knowledge panels
        - People Also Ask
        - Related searches
        - Sponsored results
        
        Args:
            data: Raw Google SERP response
        
        Returns:
            Normalized dict with structured SERP data
        """
        if not isinstance(data, (dict, str)):
            return {"results": []}
        
        # If data is HTML string, return as-is for now
        # (Bright Data's SERP API typically returns structured JSON)
        if isinstance(data, str):
            return {
                "results": [],
                "raw_html": data,
            }
        
        # Extract organic results
        results = []
        organic = data.get("organic", [])
        
        for i, item in enumerate(organic, 1):
            results.append({
                "position": i,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "displayed_url": item.get("displayed_url", ""),
            })
        
        normalized = {
            "results": results,
            "total_results": data.get("total_results"),
            "search_info": data.get("search_information", {}),
        }
        
        # Add SERP features if present
        if "featured_snippet" in data:
            normalized["featured_snippet"] = data["featured_snippet"]
        
        if "knowledge_panel" in data:
            normalized["knowledge_panel"] = data["knowledge_panel"]
        
        if "people_also_ask" in data:
            normalized["people_also_ask"] = data["people_also_ask"]
        
        if "related_searches" in data:
            normalized["related_searches"] = data["related_searches"]
        
        if "ads" in data:
            normalized["ads"] = data["ads"]
        
        return normalized


class BingSERPService(BaseSERPService):
    """
    Bing Search Engine Results Page service.
    
    Placeholder for future Bing SERP implementation.
    """
    
    SEARCH_ENGINE = "bing"
    
    def _build_search_url(
        self,
        query: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> str:
        """Build Bing search URL."""
        encoded_query = quote_plus(query)
        url = f"https://www.bing.com/search?q={encoded_query}"
        
        # Add count parameter
        url += f"&count={num_results}"
        
        # Add market (language_COUNTRY format)
        if location:
            market = f"{language}_{self._parse_location_to_code(location)}"
            url += f"&mkt={market}"
        
        return url
    
    def _parse_location_to_code(self, location: str) -> str:
        """Parse location to Bing market code."""
        # Simplified - use same logic as Google for now
        if len(location) == 2:
            return location.upper()
        
        location_map = {
            "united states": "US",
            "united kingdom": "GB",
            "canada": "CA",
        }
        
        return location_map.get(location.lower(), "US")


class YandexSERPService(BaseSERPService):
    """
    Yandex Search Engine Results Page service.
    
    Placeholder for future Yandex SERP implementation.
    """
    
    SEARCH_ENGINE = "yandex"
    
    def _build_search_url(
        self,
        query: str,
        location: Optional[str],
        language: str,
        device: str,
        num_results: int,
        **kwargs
    ) -> str:
        """Build Yandex search URL."""
        encoded_query = quote_plus(query)
        url = f"https://yandex.com/search/?text={encoded_query}"
        
        # Add number of results
        url += f"&numdoc={num_results}"
        
        # Add language/region
        if location:
            region_code = self._parse_location_to_code(location)
            url += f"&lr={region_code}"
        
        return url
    
    def _parse_location_to_code(self, location: str) -> str:
        """Parse location to Yandex region code."""
        # Yandex uses numeric region IDs
        # Simplified mapping
        region_map = {
            "russia": "225",
            "ukraine": "187",
            "belarus": "149",
        }
        
        return region_map.get(location.lower(), "225")  # Default to Russia
