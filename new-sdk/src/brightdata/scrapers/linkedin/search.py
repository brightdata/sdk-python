"""
LinkedIn Search Service - Discovery/parameter-based operations.

Implements:
- client.search.linkedin.posts() - Discover posts by profile and date range
- client.search.linkedin.profiles() - Find profiles by name
- client.search.linkedin.jobs() - Find jobs by keyword/location/filters
"""

import asyncio
from typing import Union, List, Optional, Dict, Any
from datetime import datetime, timezone

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError, APIError


class LinkedInSearchService:
    """
    LinkedIn Search Service for parameter-based discovery.
    
    Provides discovery methods that search LinkedIn by parameters
    rather than extracting from specific URLs.
    
    Example:
        >>> search = LinkedInSearchService(bearer_token="token")
        >>> result = search.jobs(
        ...     keyword="python developer",
        ...     location="New York",
        ...     remote=True
        ... )
    """
    
    # Dataset IDs for different LinkedIn types
    DATASET_ID_POSTS = "gd_lwae11111pwxp6c4ea"
    DATASET_ID_PROFILES = "gd_l1oojb10z2jye29kh"
    DATASET_ID_JOBS = "gd_lj4v2v5oqpp3qb79j"
    
    TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
    STATUS_URL = "https://api.brightdata.com/datasets/v3/progress"
    RESULT_URL = "https://api.brightdata.com/datasets/v3/snapshot"
    
    def __init__(self, bearer_token: str):
        """Initialize LinkedIn search service."""
        self.bearer_token = bearer_token
        self.engine = AsyncEngine(bearer_token)
    
    # ============================================================================
    # POSTS DISCOVERY (by profile + date range)
    # ============================================================================
    
    async def posts_async(
        self,
        profile_url: Union[str, List[str]],
        start_date: Optional[Union[str, List[str]]] = None,
        end_date: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Discover posts from LinkedIn profile(s) within date range.
        
        Args:
            profile_url: Profile URL(s) to get posts from (required)
            start_date: Start date in yyyy-mm-dd format (optional)
            end_date: End date in yyyy-mm-dd format (optional)
            timeout: Operation timeout in seconds
        
        Returns:
            ScrapeResult with discovered posts
        
        Example:
            >>> result = await search.posts_async(
            ...     profile_url="https://linkedin.com/in/johndoe",
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31"
            ... )
        """
        # Normalize to lists
        profile_urls = [profile_url] if isinstance(profile_url, str) else profile_url
        start_dates = self._normalize_param(start_date, len(profile_urls))
        end_dates = self._normalize_param(end_date, len(profile_urls))
        
        # Build payload
        payload = []
        for i, url in enumerate(profile_urls):
            item: Dict[str, Any] = {"profile_url": url}
            
            if start_dates and i < len(start_dates):
                item["start_date"] = start_dates[i]
            if end_dates and i < len(end_dates):
                item["end_date"] = end_dates[i]
            
            payload.append(item)
        
        # Execute search
        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout
        )
    
    def posts(
        self,
        profile_url: Union[str, List[str]],
        start_date: Optional[Union[str, List[str]]] = None,
        end_date: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Discover posts from profile(s) (sync).
        
        See posts_async() for documentation.
        """
        return asyncio.run(self.posts_async(profile_url, start_date, end_date, timeout))
    
    # ============================================================================
    # PROFILES DISCOVERY (by name)
    # ============================================================================
    
    async def profiles_async(
        self,
        firstName: Union[str, List[str]],
        lastName: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Find LinkedIn profiles by name.
        
        Args:
            firstName: First name(s) to search (required)
            lastName: Last name(s) to search (optional)
            timeout: Operation timeout in seconds
        
        Returns:
            ScrapeResult with matching profiles
        
        Example:
            >>> result = await search.profiles_async(
            ...     firstName="John",
            ...     lastName="Doe"
            ... )
        """
        # Normalize to lists
        first_names = [firstName] if isinstance(firstName, str) else firstName
        last_names = self._normalize_param(lastName, len(first_names))
        
        # Build payload
        payload = []
        for i, first_name in enumerate(first_names):
            item: Dict[str, Any] = {"firstName": first_name}
            
            if last_names and i < len(last_names):
                item["lastName"] = last_names[i]
            
            payload.append(item)
        
        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_PROFILES,
            timeout=timeout
        )
    
    def profiles(
        self,
        firstName: Union[str, List[str]],
        lastName: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Find profiles by name (sync).
        
        See profiles_async() for documentation.
        """
        return asyncio.run(self.profiles_async(firstName, lastName, timeout))
    
    # ============================================================================
    # JOBS DISCOVERY (by keyword + extensive filters)
    # ============================================================================
    
    async def jobs_async(
        self,
        url: Optional[Union[str, List[str]]] = None,
        location: Optional[Union[str, List[str]]] = None,
        keyword: Optional[Union[str, List[str]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeRange: Optional[Union[str, List[str]]] = None,
        jobType: Optional[Union[str, List[str]]] = None,
        experienceLevel: Optional[Union[str, List[str]]] = None,
        remote: Optional[bool] = None,
        company: Optional[Union[str, List[str]]] = None,
        locationRadius: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Discover LinkedIn jobs by criteria.
        
        Args:
            url: Job search URL or company URL (optional)
            location: Location filter(s)
            keyword: Job keyword(s)
            country: Country code(s) - 2-letter format
            timeRange: Time range filter(s)
            jobType: Job type filter(s) (e.g., "full-time", "contract")
            experienceLevel: Experience level(s) (e.g., "entry", "mid", "senior")
            remote: Remote jobs only
            company: Company name filter(s)
            locationRadius: Location radius filter(s)
            timeout: Operation timeout in seconds
        
        Returns:
            ScrapeResult with matching jobs
        
        Example:
            >>> result = await search.jobs_async(
            ...     keyword="python developer",
            ...     location="New York",
            ...     remote=True,
            ...     experienceLevel="mid"
            ... )
        """
        # At least one search criteria required
        if not any([url, location, keyword, country, company]):
            raise ValidationError(
                "At least one search parameter required "
                "(url, location, keyword, country, or company)"
            )
        
        # Determine batch size (use longest list)
        batch_size = 1
        if url and isinstance(url, list):
            batch_size = max(batch_size, len(url))
        if keyword and isinstance(keyword, list):
            batch_size = max(batch_size, len(keyword))
        if location and isinstance(location, list):
            batch_size = max(batch_size, len(location))
        
        # Normalize all parameters to lists
        urls = self._normalize_param(url, batch_size)
        locations = self._normalize_param(location, batch_size)
        keywords = self._normalize_param(keyword, batch_size)
        countries = self._normalize_param(country, batch_size)
        time_ranges = self._normalize_param(timeRange, batch_size)
        job_types = self._normalize_param(jobType, batch_size)
        experience_levels = self._normalize_param(experienceLevel, batch_size)
        companies = self._normalize_param(company, batch_size)
        location_radii = self._normalize_param(locationRadius, batch_size)
        
        # Build payload
        payload = []
        for i in range(batch_size):
            item: Dict[str, Any] = {}
            
            if urls and i < len(urls):
                item["url"] = urls[i]
            if locations and i < len(locations):
                item["location"] = locations[i]
            if keywords and i < len(keywords):
                item["keyword"] = keywords[i]
            if countries and i < len(countries):
                item["country"] = countries[i]
            if time_ranges and i < len(time_ranges):
                item["timeRange"] = time_ranges[i]
            if job_types and i < len(job_types):
                item["jobType"] = job_types[i]
            if experience_levels and i < len(experience_levels):
                item["experienceLevel"] = experience_levels[i]
            if remote is not None:
                item["remote"] = remote
            if companies and i < len(companies):
                item["company"] = companies[i]
            if location_radii and i < len(location_radii):
                item["locationRadius"] = location_radii[i]
            
            payload.append(item)
        
        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_JOBS,
            timeout=timeout
        )
    
    def jobs(
        self,
        url: Optional[Union[str, List[str]]] = None,
        location: Optional[Union[str, List[str]]] = None,
        keyword: Optional[Union[str, List[str]]] = None,
        country: Optional[Union[str, List[str]]] = None,
        timeRange: Optional[Union[str, List[str]]] = None,
        jobType: Optional[Union[str, List[str]]] = None,
        experienceLevel: Optional[Union[str, List[str]]] = None,
        remote: Optional[bool] = None,
        company: Optional[Union[str, List[str]]] = None,
        locationRadius: Optional[Union[str, List[str]]] = None,
        timeout: int = 180,
    ) -> ScrapeResult:
        """
        Discover jobs (sync).
        
        See jobs_async() for full documentation.
        
        Example:
            >>> result = search.jobs(
            ...     keyword="python",
            ...     location="NYC",
            ...     remote=True
            ... )
        """
        return asyncio.run(self.jobs_async(
            url=url,
            location=location,
            keyword=keyword,
            country=country,
            timeRange=timeRange,
            jobType=jobType,
            experienceLevel=experienceLevel,
            remote=remote,
            company=company,
            locationRadius=locationRadius,
            timeout=timeout
        ))
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _normalize_param(
        self,
        param: Optional[Union[str, List[str]]],
        target_length: int
    ) -> Optional[List[str]]:
        """
        Normalize parameter to list.
        
        Args:
            param: String or list of strings
            target_length: Desired list length
        
        Returns:
            List of strings, or None if param is None
        """
        if param is None:
            return None
        
        if isinstance(param, str):
            # Repeat single value for batch
            return [param] * target_length
        
        return param
    
    async def _execute_search(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        timeout: int,
    ) -> ScrapeResult:
        """
        Execute search operation via trigger/poll/fetch.
        
        Args:
            payload: Search parameters
            dataset_id: LinkedIn dataset ID
            timeout: Operation timeout
        
        Returns:
            ScrapeResult with search results
        """
        request_sent_at = datetime.now(timezone.utc)
        
        async with self.engine:
            # Trigger search
            snapshot_id = await self._trigger_async(payload, dataset_id)
            
            if not snapshot_id:
                return ScrapeResult(
                    success=False,
                    url="",
                    status="error",
                    error="Failed to trigger search - no snapshot_id returned",
                    platform="linkedin",
                    request_sent_at=request_sent_at,
                    data_received_at=datetime.now(timezone.utc),
                )
            
            snapshot_id_received_at = datetime.now(timezone.utc)
            
            # Poll and fetch
            result = await self._poll_and_fetch_async(
                snapshot_id=snapshot_id,
                poll_interval=10,
                poll_timeout=timeout,
                request_sent_at=request_sent_at,
                snapshot_id_received_at=snapshot_id_received_at,
            )
            
            return result
    
    async def _trigger_async(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
    ) -> Optional[str]:
        """Trigger search and get snapshot_id."""
        params = {
            "dataset_id": dataset_id,
            "include_errors": "true",
        }
        
        async with self.engine._session.post(
            self.TRIGGER_URL,
            json=payload,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("snapshot_id")
            else:
                error_text = await response.text()
                raise APIError(
                    f"Trigger failed (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )
    
    async def _poll_and_fetch_async(
        self,
        snapshot_id: str,
        poll_interval: int,
        poll_timeout: int,
        request_sent_at: datetime,
        snapshot_id_received_at: datetime,
    ) -> ScrapeResult:
        """
        Poll until ready and fetch results.
        
        Uses shared polling utility for consistent behavior across services.
        """
        from ...utils.polling import poll_until_ready
        
        return await poll_until_ready(
            get_status_func=self._get_status_async,
            fetch_result_func=self._fetch_result_async,
            snapshot_id=snapshot_id,
            poll_interval=poll_interval,
            poll_timeout=poll_timeout,
            request_sent_at=request_sent_at,
            snapshot_id_received_at=snapshot_id_received_at,
            platform="linkedin",
            cost_per_record=0.002,  # LinkedIn cost
        )
    
    async def _get_status_async(self, snapshot_id: str) -> str:
        """Get snapshot status."""
        url = f"{self.STATUS_URL}/{snapshot_id}"
        
        async with self.engine._session.get(
            url,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("status", "unknown")
            return "error"
    
    async def _fetch_result_async(self, snapshot_id: str) -> Any:
        """Fetch snapshot results."""
        url = f"{self.RESULT_URL}/{snapshot_id}"
        params = {"format": "json"}
        
        async with self.engine._session.get(
            url,
            params=params,
            headers=self.engine._session.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise APIError(
                    f"Failed to fetch results (HTTP {response.status}): {error_text}",
                    status_code=response.status
                )

