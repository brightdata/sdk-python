"""
LinkedIn Search Scraper - Discovery/parameter-based operations.

Implements:
- client.search.linkedin.posts()          - Discover posts by profile and date range (async)
- client.search.linkedin.posts_sync()     - Discover posts by profile and date range (sync)
- client.search.linkedin.profiles()       - Find profiles by name (async)
- client.search.linkedin.profiles_sync()  - Find profiles by name (sync)
- client.search.linkedin.jobs()           - Find jobs by keyword/location/filters (async)
- client.search.linkedin.jobs_sync()      - Find jobs by keyword/location/filters (sync)
"""

import asyncio
from typing import Union, List, Optional, Dict, Any

from ...core.engine import AsyncEngine
from ...models import ScrapeResult
from ...exceptions import ValidationError
from ...utils.function_detection import get_caller_function_name
from ...constants import DEFAULT_POLL_INTERVAL, DEFAULT_TIMEOUT_SHORT, COST_PER_RECORD_LINKEDIN
from ..api_client import DatasetAPIClient
from ..workflow import WorkflowExecutor


class LinkedInSearchScraper:
    """
    LinkedIn Search Scraper for parameter-based discovery.

    Provides discovery methods that search LinkedIn by parameters
    rather than extracting from specific URLs. This is a parallel component
    to LinkedInScraper, both doing LinkedIn data extraction but with
    different approaches (parameter-based vs URL-based).

    Example:
        >>> scraper = LinkedInSearchScraper(bearer_token="token")
        >>>
        >>> # Async
        >>> result = await scraper.jobs(
        ...     keyword="python developer",
        ...     location="New York",
        ...     remote=True
        ... )
        >>>
        >>> # Sync
        >>> result = scraper.jobs_sync(
        ...     keyword="python developer",
        ...     location="New York"
        ... )
    """

    # Dataset IDs for different LinkedIn types
    DATASET_ID_POSTS = "gd_lyy3tktm25m4avu764"
    DATASET_ID_PROFILES = "gd_l1viktl72bvl7bjuj0"  # URL-based profile scraping
    DATASET_ID_PROFILES_DISCOVERY = "gd_m8d03he47z8nwb5xc"  # Name-based profile search
    DATASET_ID_JOBS = "gd_lpfll7v5hcqtkxl6l"  # URL-based job scraping
    DATASET_ID_JOBS_DISCOVERY = "gd_m487ihp32jtc4ujg45"  # Keyword/location discovery

    def __init__(self, bearer_token: str, engine: Optional[AsyncEngine] = None):
        """
        Initialize LinkedIn search scraper.

        Args:
            bearer_token: Bright Data API token
            engine: Optional AsyncEngine instance. If not provided, creates a new one.
                    Allows dependency injection for testing and flexibility.
        """
        self.bearer_token = bearer_token
        self.engine = engine if engine is not None else AsyncEngine(bearer_token)
        self.api_client = DatasetAPIClient(self.engine)
        self.workflow_executor = WorkflowExecutor(
            api_client=self.api_client,
            platform_name="linkedin",
            cost_per_record=COST_PER_RECORD_LINKEDIN,
        )

    # ============================================================================
    # POSTS DISCOVERY (by profile + date range)
    # ============================================================================

    async def posts(
        self,
        url: Union[str, List[str]],
        start_date: Optional[Union[str, List[str]]] = None,
        end_date: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover posts from LinkedIn profile(s) within date range.

        Args:
            url: Profile URL(s) to get posts from (required)
            start_date: Start date in yyyy-mm-dd format (optional)
            end_date: End date in yyyy-mm-dd format (optional)
            timeout: Operation timeout in seconds

        Returns:
            ScrapeResult with discovered posts

        Example:
            >>> result = await search.posts(
            ...     url="https://linkedin.com/in/johndoe",
            ...     start_date="2025-01-01",
            ...     end_date="2025-12-31"
            ... )
        """
        # Normalize to lists
        profile_urls = [url] if isinstance(url, str) else url
        start_dates = self._normalize_param(start_date, len(profile_urls))
        end_dates = self._normalize_param(end_date, len(profile_urls))

        # Build payload - API requires "url" field, not "profile_url"
        payload = []
        for i, profile_url in enumerate(profile_urls):
            item: Dict[str, Any] = {"url": profile_url}

            if start_dates and i < len(start_dates):
                item["start_date"] = start_dates[i]
            if end_dates and i < len(end_dates):
                item["end_date"] = end_dates[i]

            payload.append(item)

        # Execute search with discovery params
        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_POSTS,
            timeout=timeout,
            extra_params={"type": "discover_new", "discover_by": "profile_url"},
        )

    def posts_sync(
        self,
        url: Union[str, List[str]],
        start_date: Optional[Union[str, List[str]]] = None,
        end_date: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover posts from profile(s) (sync version).

        See posts() for documentation.
        """

        async def _run():
            async with self.engine:
                return await self.posts(url, start_date, end_date, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # PROFILES DISCOVERY (by name)
    # ============================================================================

    async def profiles(
        self,
        first_name: Union[str, List[str]],
        last_name: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Find LinkedIn profiles by name.

        Args:
            first_name: First name(s) to search (required)
            last_name: Last name(s) to search (optional)
            timeout: Operation timeout in seconds

        Returns:
            ScrapeResult with matching profiles

        Example:
            >>> result = await search.profiles(
            ...     first_name="John",
            ...     last_name="Doe"
            ... )
        """
        # Normalize to lists
        first_names = [first_name] if isinstance(first_name, str) else first_name
        last_names = self._normalize_param(last_name, len(first_names))

        # Build payload - API requires url + first_name + last_name
        payload = []
        for i, fname in enumerate(first_names):
            item: Dict[str, Any] = {
                "url": "https://www.linkedin.com",
                "first_name": fname,
            }

            if last_names and i < len(last_names):
                item["last_name"] = last_names[i]

            payload.append(item)

        return await self._execute_search(
            payload=payload, dataset_id=self.DATASET_ID_PROFILES_DISCOVERY, timeout=timeout
        )

    def profiles_sync(
        self,
        first_name: Union[str, List[str]],
        last_name: Optional[Union[str, List[str]]] = None,
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Find profiles by name (sync version).

        See profiles() for documentation.
        """

        async def _run():
            async with self.engine:
                return await self.profiles(first_name, last_name, timeout)

        return asyncio.run(_run())

    # ============================================================================
    # JOBS DISCOVERY (by keyword + extensive filters)
    # ============================================================================

    async def jobs(
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
        timeout: int = DEFAULT_TIMEOUT_SHORT,
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
            >>> result = await search.jobs(
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

        # Build payload based on input type
        # - If URL provided: use URL-based dataset (for scraping specific job pages)
        # - If keyword/location provided: use discovery dataset (for searching jobs)
        payload = []
        use_discovery = False

        for i in range(batch_size):
            # If URL provided directly, use it with URL-based scraper
            if urls and i < len(urls):
                item = {"url": urls[i]}
            else:
                # Use discovery dataset with keyword/location parameters
                use_discovery = True
                item: Dict[str, Any] = {}

                if keywords and i < len(keywords):
                    item["keyword"] = keywords[i]
                if locations and i < len(locations):
                    item["location"] = locations[i]
                if countries and i < len(countries):
                    item["country"] = countries[i]
                if time_ranges and i < len(time_ranges):
                    item["time_range"] = time_ranges[i]
                if job_types and i < len(job_types):
                    item["job_type"] = job_types[i]
                if experience_levels and i < len(experience_levels):
                    item["experience_level"] = experience_levels[i]
                if remote is not None:
                    item["remote"] = remote
                if companies and i < len(companies):
                    item["company"] = companies[i]
                if location_radii and i < len(location_radii):
                    item["location_radius"] = location_radii[i]

            payload.append(item)

        # Use same dataset for both URL-based and keyword-based, but with different query params
        # For keyword search: add type=discover_new&discover_by=keyword
        extra_params = {"type": "discover_new", "discover_by": "keyword"} if use_discovery else None

        return await self._execute_search(
            payload=payload,
            dataset_id=self.DATASET_ID_JOBS,
            timeout=timeout,
            extra_params=extra_params,
        )

    def jobs_sync(
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
        timeout: int = DEFAULT_TIMEOUT_SHORT,
    ) -> ScrapeResult:
        """
        Discover jobs (sync version).

        See jobs() for full documentation.
        """

        async def _run():
            async with self.engine:
                return await self.jobs(
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
                    timeout=timeout,
                )

        return asyncio.run(_run())

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _normalize_param(
        self, param: Optional[Union[str, List[str]]], target_length: int
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

    def _build_linkedin_jobs_search_url(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        country: Optional[str] = None,
        time_range: Optional[str] = None,
        job_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        remote: Optional[bool] = None,
        company: Optional[str] = None,
        location_radius: Optional[str] = None,
    ) -> str:
        """
        Build LinkedIn job search URL from parameters.

        LinkedIn API requires URLs, not raw search parameters.
        This method constructs a valid LinkedIn job search URL from the provided filters.

        Args:
            keyword: Job keyword/title
            location: Location name
            country: Country code
            time_range: Time range filter
            job_type: Job type filter
            experience_level: Experience level filter
            remote: Remote jobs only
            company: Company name filter
            location_radius: Location radius filter

        Returns:
            LinkedIn job search URL

        Example:
            >>> _build_linkedin_jobs_search_url(
            ...     keyword="python developer",
            ...     location="New York",
            ...     remote=True
            ... )
            'https://www.linkedin.com/jobs/search/?keywords=python%20developer&location=New%20York&f_WT=2'
        """
        from urllib.parse import urlencode

        base_url = "https://www.linkedin.com/jobs/search/"
        params = {}

        # Keywords
        if keyword:
            params["keywords"] = keyword

        # Location
        if location:
            params["location"] = location

        # Remote work type (f_WT: 1=on-site, 2=remote, 3=hybrid)
        if remote:
            params["f_WT"] = "2"

        # Experience level (f_E: 1=internship, 2=entry, 3=associate, 4=mid-senior, 5=director, 6=executive)
        if experience_level:
            level_map = {
                "internship": "1",
                "entry": "2",
                "associate": "3",
                "mid": "4",
                "mid-senior": "4",
                "senior": "4",
                "director": "5",
                "executive": "6",
            }
            if experience_level.lower() in level_map:
                params["f_E"] = level_map[experience_level.lower()]

        # Job type (f_JT: F=full-time, P=part-time, C=contract, T=temporary, I=internship, V=volunteer, O=other)
        if job_type:
            type_map = {
                "full-time": "F",
                "full time": "F",
                "part-time": "P",
                "part time": "P",
                "contract": "C",
                "temporary": "T",
                "internship": "I",
                "volunteer": "V",
            }
            if job_type.lower() in type_map:
                params["f_JT"] = type_map[job_type.lower()]

        # Time range (f_TPR: r86400=past 24h, r604800=past week, r2592000=past month)
        if time_range:
            time_map = {
                "day": "r86400",
                "past-day": "r86400",
                "24h": "r86400",
                "week": "r604800",
                "past-week": "r604800",
                "month": "r2592000",
                "past-month": "r2592000",
            }
            if time_range.lower() in time_map:
                params["f_TPR"] = time_map[time_range.lower()]

        # Company (f_C)
        if company:
            params["f_C"] = company

        # Build URL
        if params:
            url = f"{base_url}?{urlencode(params)}"
        else:
            url = base_url

        return url

    async def _execute_search(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        timeout: int,
        extra_params: Optional[Dict[str, str]] = None,
    ) -> ScrapeResult:
        """
        Execute search operation via trigger/poll/fetch.

        Args:
            payload: Search parameters
            dataset_id: LinkedIn dataset ID
            timeout: Operation timeout
            extra_params: Additional query parameters (e.g., type, discover_by)

        Returns:
            ScrapeResult with search results
        """
        # Use workflow executor for trigger/poll/fetch
        sdk_function = get_caller_function_name()

        result = await self.workflow_executor.execute(
            payload=payload,
            dataset_id=dataset_id,
            poll_interval=DEFAULT_POLL_INTERVAL,
            poll_timeout=timeout,
            include_errors=True,
            sdk_function=sdk_function,
            extra_params=extra_params,
        )

        return result
