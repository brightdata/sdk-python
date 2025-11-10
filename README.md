# BRIGHTDATA PYTHON SDK - WORLD-CLASS REFACTORING PLAN
## 100/100 Enterprise-Grade SDK Development Strategy

---

## EXECUTIVE SUMMARY

This plan outlines the complete refactoring of the BrightData Python SDK from a monolithic, synchronous implementation to a world-class, async-first, modular architecture. Based on analysis of three codebases:

- **old-sdk**: Current production SDK with architectural issues
- **ref-sdk**: Reference implementation with best practices
- **new-sdk**: Target for world-class implementation (this project)

**Goal**: Create a production-ready SDK that combines the simplicity of `old-sdk` with the power and architecture of `ref-sdk`, following FAANG-level best practices.

------------

## DETAILED COMPARISON: 3 REPOS ANALYSIS

### 1. OLD-SDK (Current Production) - Critical Issues

#### Architecture Problems
```
❌ Monolithic client.py (897 lines)
❌ Synchronous-only with ThreadPoolExecutor
❌ No separation of concerns
❌ Hardcoded timeouts (DEFAULT_TIMEOUT = 65 vs docs say 30)
❌ No interface/protocol definitions
```

#### What Works Well
```
✅ Comprehensive docstrings
✅ Input validation
✅ Zone auto-creation
✅ Structured logging
✅ Error handling with custom exceptions
```

#### File Structure
```
old-sdk/
├── brightdata/
│   ├── __init__.py (82 lines - clean exports)
│   ├── client.py (897 lines - TOO LARGE, monolithic)
│   ├── api/
│   │   ├── scraper.py (205 lines - sync only)
│   │   ├── search.py (similar issues)
│   │   ├── chatgpt.py
│   │   ├── linkedin.py
│   │   ├── crawl.py
│   │   └── extract.py
│   ├── exceptions/
│   │   └── errors.py (good hierarchy)
│   └── utils/
│       ├── validation.py
│       ├── retry.py
│       ├── zone_manager.py
│       └── logging_config.py (177 lines - over-engineered)
```

**Key Problems**:
1. No async support at all
2. Client does too much (897 lines)
3. API modules tightly coupled to requests library
4. No registry pattern for extensibility
5. ThreadPoolExecutor waterfall pattern (slow)
6. No result objects (returns raw dict/str)

---

### 2. REF-SDK (Reference Implementation) - Excellence

#### Architecture Strengths
```
✅ Async-first with sync wrappers
✅ Registry pattern for auto-discovery
✅ Rich result objects (ScrapeResult, CrawlResult)
✅ Clear separation: Engine → Scraper → Auto
✅ Fallback chain (Specialized → Browser → Web Unlocker)
✅ Connection pooling & concurrency strategies
```

#### File Structure
```
ref-sdk/
└── brightdata/
    ├── __init__.py (11 lines - clean)
    ├── auto.py (471 lines - simplified API)
    ├── models.py (268 lines - dataclasses)
    ├── browserapi/
    │   ├── browser_api.py
    │   ├── browser_pool.py
    │   └── playwright_session.py
    ├── crawlerapi/
    │   └── crawler_api.py
    ├── webscraper_api/
    │   ├── base_specialized_scraper.py (212 lines)
    │   ├── engine.py
    │   ├── registry.py (53 lines - brilliant)
    │   ├── scrapers/
    │   │   ├── amazon/
    │   │   ├── linkedin/
    │   │   ├── instagram/
    │   │   ├── reddit/
    │   │   ├── tiktok/
    │   │   ├── x/
    │   │   └── youtube/
    │   └── utils/
    │       ├── async_poll.py
    │       ├── concurrent_trigger.py
    │       └── poll.py
    └── utils/
        └── utils.py
```

**What Makes It World-Class**:
1. **Async-first**: Native asyncio + aiohttp, sync wrappers for compatibility
2. **Registry pattern**: `@register("amazon")` decorator for auto-discovery
3. **Result objects**: `ScrapeResult` with timing, cost, metadata
4. **Layered API**: Simple `scrape_url()` → Complex specialized scrapers
5. **Intelligent fallback**: Automatic Browser API fallback when no scraper
6. **Connection pooling**: BrowserPool for efficient resource usage
7. **Philosophy-driven**: Clear design principles documented

---

### 3. BRIGHTDATA API (Reference Documentation)

Based on https://brightdata.com/ and https://docs.brightdata.com/api-reference/SDK:

#### Core APIs to Support
```
1. Web Unlocker API - Scrape any URL (bypass anti-bot)
2. SERP API - Google/Bing/Yandex search results
3. Web Crawl API - Discover and crawl entire domains
4. Browser API - Remote browser automation (Playwright/Puppeteer/Selenium)
5. Datasets API - Specialized scrapers (LinkedIn, Amazon, etc.)
6. Proxy Services - Direct proxy access (optional)
```

---

## WORLD-CLASS SDK ARCHITECTURE

### Design Principles (FAANG-Level)

1. **Async-First, Sync-Friendly**
   - All core operations async by default
   - Sync wrappers using `asyncio.run()` or thread pools
   - No blocking in async contexts

2. **Progressive Disclosure**
   - Simple: `scrape_url("https://amazon.com/...")` → done
   - Intermediate: `client.scrape(url, zone=..., country=...)`
   - Advanced: Direct scraper classes with full control

3. **Separation of Concerns**
   - **Engine Layer**: HTTP client, API communication
   - **Core Layer**: Main client, zone management
   - **API Layer**: Specialized APIs (scrape, search, crawl, browser)
   - **Scraper Layer**: Platform-specific scrapers
   - **Auto Layer**: Simplified "magic" functions
   - **Utils Layer**: Shared utilities

4. **Registry Pattern for Extensibility**
   - Scrapers self-register with `@register("domain")`
   - URL pattern matching for auto-routing
   - Easy to add new scrapers without core changes

5. **Rich Result Objects**
   - Never return raw dicts/strings
   - Always use `ScrapeResult`, `CrawlResult`, etc.
   - Include timing, cost, metadata, methods

6. **Type Safety**
   - Full type hints everywhere
   - Protocol classes for interfaces
   - Runtime validation with Pydantic (optional)

7. **Observability**
   - Structured logging
   - Timing metrics on all operations
   - Cost tracking
   - Event hooks for monitoring

8. **Error Handling**
   - Custom exception hierarchy
   - Never swallow errors
   - Detailed error messages with context
   - Retry logic with exponential backoff

---

## PROPOSED FILE STRUCTURE

> **Note**: This structure has been refined based on industry best practices analysis. Key improvements:
> - Removed redundant `core/session.py` (engine manages sessions)
> - Renamed `api/scraper.py` → `api/web_unlocker.py` for clarity
> - Renamed `api/search.py` → `api/serp.py` for clarity
> - Moved `browser/` → `api/browser/` for consistency
> - Added `config.py` for centralized configuration (Pydantic Settings)
> - Added `types.py` for type aliases
> - Added `core/hooks.py` for event system
> - Added `core/logging.py` for structured logging
> - Added `py.typed` marker for PEP 561 type stubs
> - Added `.pre-commit-config.yaml` for code quality

```
new-sdk/
├── README.md                           # Comprehensive documentation
├── LICENSE                             # MIT License
├── CHANGELOG.md                        # Version history
├── pyproject.toml                      # Modern Python packaging (PEP 518)
├── setup.py                            # Backward compatibility
├── requirements.txt                    # Runtime dependencies
├── requirements-dev.txt                # Development dependencies
├── .gitignore
├── .pre-commit-config.yaml             # Pre-commit hooks
├── .github/
│   └── workflows/
│       ├── test.yml                    # CI/CD pipeline
│       ├── publish.yml                 # PyPI publishing
│       └── lint.yml                    # Code quality
│
├── src/                                # Modern src/ layout
│   └── brightdata/
│       ├── __init__.py                 # Main exports
│       ├── _version.py                 # Version management
│       ├── py.typed                    # PEP 561 type stubs marker
│       │
│       ├── client.py                   # Main BrightData client (slim)
│       ├── auto.py                     # Simplified API (scrape_url, etc.)
│       ├── config.py                   # Configuration (Pydantic Settings)
│       ├── types.py                    # Type aliases and unions
│       ├── models.py                   # Result objects (dataclasses)
│       ├── protocols.py                # Interface definitions (typing.Protocol)
│       ├── constants.py                # Shared constants
│       │
│       ├── core/                       # Core infrastructure
│       │   ├── __init__.py
│       │   ├── engine.py               # HTTP client (aiohttp-based, manages sessions)
│       │   ├── auth.py                 # Authentication handling
│       │   ├── zone_manager.py         # Zone operations
│       │   ├── hooks.py                # Event hooks system
│       │   └── logging.py              # Structured logging
│       │
│       ├── api/                        # API implementations
│       │   ├── __init__.py
│       │   ├── base.py                 # Base API class
│       │   ├── web_unlocker.py         # Web Unlocker API (renamed from scraper.py)
│       │   ├── serp.py                 # SERP API (renamed from search.py)
│       │   ├── crawl.py                # Web Crawl API
│       │   ├── datasets.py             # Datasets API
│       │   ├── download.py             # Download/snapshot operations
│       │   └── browser/                # Browser API (moved from browser/)
│       │       ├── __init__.py
│       │       ├── browser_api.py      # Main browser API
│       │       ├── browser_pool.py     # Connection pooling
│       │       ├── config.py           # Browser configuration
│       │       └── session.py          # Browser sessions
│       │
│       ├── scrapers/                   # Specialized scrapers
│       │   ├── __init__.py
│       │   ├── base.py                 # Base scraper class
│       │   ├── registry.py             # Registry pattern
│       │   ├── amazon/
│       │   │   ├── __init__.py
│       │   │   └── scraper.py
│       │   ├── linkedin/
│       │   │   ├── __init__.py
│       │   │   ├── scraper.py
│       │   │   ├── profiles.py
│       │   │   ├── companies.py
│       │   │   └── jobs.py
│       │   ├── chatgpt/
│       │   │   ├── __init__.py
│       │   │   └── scraper.py
│       │   └── ...                     # Other platforms
│       │
│       ├── utils/                      # Utilities
│       │   ├── __init__.py
│       │   ├── validation.py           # Input validation
│       │   ├── retry.py                # Retry logic
│       │   ├── polling.py              # Async/sync polling
│       │   ├── parsing.py              # Content parsing
│       │   ├── timing.py               # Performance measurement
│       │   └── url.py                  # URL utilities
│       │
│       ├── exceptions/                 # Custom exceptions
│       │   ├── __init__.py
│       │   └── errors.py               # Exception hierarchy
│       │
│       └── _internal/                  # Private implementation details
│           ├── __init__.py
│           └── compat.py               # Python version compatibility (if needed)
│
├── tests/                              # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   │
│   ├── unit/                           # Unit tests
│   │   ├── test_client.py
│   │   ├── test_engine.py
│   │   ├── test_validation.py
│   │   ├── test_retry.py
│   │   └── test_models.py
│   │
│   ├── integration/                    # Integration tests
│   │   ├── test_web_unlocker_api.py
│   │   ├── test_serp_api.py
│   │   ├── test_crawl_api.py
│   │   └── test_browser_api.py
│   │
│   ├── e2e/                            # End-to-end tests
│   │   ├── test_simple_scrape.py
│   │   ├── test_batch_scrape.py
│   │   └── test_async_operations.py
│   │
│   └── fixtures/                       # Test data
│       ├── responses/
│       └── mock_data/
│
├── examples/                           # Usage examples
│   ├── 01_simple_scrape.py
│   ├── 02_async_scrape.py
│   ├── 03_batch_scraping.py
│   ├── 04_specialized_scrapers.py
│   ├── 05_browser_automation.py
│   ├── 06_web_crawling.py
│   └── 07_advanced_usage.py
│
├── docs/                               # Documentation
│   ├── index.md
│   ├── quickstart.md
│   ├── architecture.md
│   ├── api-reference/
│   ├── guides/
│   └── contributing.md
│
└── benchmarks/                         # Performance benchmarks
    ├── bench_async_vs_sync.py
    ├── bench_batch_operations.py
    └── bench_memory_usage.py
```

---

## DETAILED IMPLEMENTATION ROADMAP

### PHASE 1: Foundation (Week 1-2)

#### 1.1 Project Setup
```python
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "brightdata-sdk"
version = "2.0.0"
description = "Modern async-first Python SDK for Bright Data APIs"
authors = [{name = "Bright Data", email = "support@brightdata.com"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "aiohttp>=3.9.0",
    "requests>=2.31.0",
    "python-dotenv>=1.0.0",
    "tldextract>=5.0.0",
    "pydantic>=2.0.0",  # For config.py Settings
    "pydantic-settings>=2.0.0",  # For environment variable support
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
]
browser = [
    "playwright>=1.40.0",
]
all = ["brightdata-sdk[dev,browser]"]
```

#### 1.2 Configuration Module
```python
# src/brightdata/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class BrightDataConfig(BaseSettings):
    """Centralized configuration for Bright Data SDK."""
    
    api_token: Optional[str] = None
    default_timeout: int = 30
    default_poll_interval: int = 10
    default_poll_timeout: int = 600
    auto_create_zones: bool = True
    web_unlocker_zone: str = "sdk_unlocker"
    serp_zone: str = "sdk_serp"
    browser_zone: str = "sdk_browser"
    
    class Config:
        env_prefix = "BRIGHTDATA_"
        case_sensitive = False
```

#### 1.3 Core Models
```python
# src/brightdata/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict

@dataclass
class ScrapeResult:
    """Comprehensive result object for scraping operations."""
    success: bool
    url: str
    status: str  # "ready" | "error" | "timeout" | "in_progress"
    data: Optional[Any] = None
    error: Optional[str] = None
    snapshot_id: Optional[str] = None
    cost: Optional[float] = None
    fallback_used: bool = False
    root_domain: Optional[str] = None
    
    # Timing metrics
    request_sent_at: Optional[datetime] = None
    snapshot_id_received_at: Optional[datetime] = None
    snapshot_polled_at: List[datetime] = field(default_factory=list)
    data_received_at: Optional[datetime] = None
    
    # Statistics
    html_char_size: Optional[int] = None
    row_count: Optional[int] = None
    field_count: Optional[int] = None
    
    def elapsed_ms(self) -> Optional[float]:
        """Calculate total elapsed time in milliseconds."""
        if self.request_sent_at and self.data_received_at:
            return (self.data_received_at - self.request_sent_at).total_seconds() * 1000
        return None
    
    def save_to_file(self, filepath: str, format: str = "json") -> None:
        """Save result data to file."""
        # Implementation

@dataclass
class CrawlResult:
    """Result object for web crawling operations."""
    # Similar structure to ScrapeResult
    # ...
```

#### 1.4 Exception Hierarchy
```python
# src/brightdata/exceptions/errors.py
class BrightDataError(Exception):
    """Base exception for all Bright Data errors."""
    pass

class ValidationError(BrightDataError):
    """Input validation failed."""
    pass

class AuthenticationError(BrightDataError):
    """Authentication or authorization failed."""
    pass

class APIError(BrightDataError):
    """API request failed."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

class TimeoutError(BrightDataError):
    """Operation timed out."""
    pass

class ZoneError(BrightDataError):
    """Zone operation failed."""
    pass

class NetworkError(BrightDataError):
    """Network connectivity issue."""
    pass
```

---

### PHASE 2: Core Engine (Week 2-3)

#### 2.1 Async HTTP Engine
```python
# src/brightdata/core/engine.py
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from ..models import ScrapeResult
from ..exceptions import APIError, AuthenticationError, TimeoutError

class AsyncEngine:
    """Async HTTP engine for all API operations."""
    
    def __init__(self, bearer_token: str, timeout: int = 30):
        self.bearer_token = bearer_token
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'brightdata-sdk/2.0.0'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()
    
    async def trigger(
        self,
        payload: List[Dict[str, Any]],
        dataset_id: str,
        include_errors: bool = True
    ) -> Optional[str]:
        """Trigger a dataset collection job."""
        url = "https://api.brightdata.com/datasets/v3/trigger"
        params = {
            "dataset_id": dataset_id,
            "include_errors": str(include_errors).lower()
        }
        
        async with self._session.post(url, json=payload, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("snapshot_id")
            elif response.status == 401:
                raise AuthenticationError("Invalid API token")
            else:
                text = await response.text()
                raise APIError(f"Trigger failed: {text}", status_code=response.status)
    
    async def get_status(self, snapshot_id: str) -> str:
        """Get snapshot status."""
        url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
        
        async with self._session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("status", "unknown")
            else:
                return "error"
    
    async def fetch_result(self, snapshot_id: str) -> ScrapeResult:
        """Fetch snapshot results."""
        url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
        
        from datetime import datetime
        data_received_at = datetime.utcnow()
        
        async with self._session.get(url, params={"format": "json"}) as response:
            if response.status == 200:
                data = await response.json()
                return ScrapeResult(
                    success=True,
                    url=url,
                    status="ready",
                    data=data,
                    snapshot_id=snapshot_id,
                    data_received_at=data_received_at
                )
            else:
                text = await response.text()
                return ScrapeResult(
                    success=False,
                    url=url,
                    status="error",
                    error=text,
                    snapshot_id=snapshot_id
                )
    
    async def poll_until_ready(
        self,
        snapshot_id: str,
        poll_interval: int = 10,
        timeout: int = 600
    ) -> ScrapeResult:
        """Poll snapshot until ready or timeout."""
        from datetime import datetime
        import asyncio
        
        start_time = datetime.utcnow()
        snapshot_polled_at = []
        
        while True:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout:
                return ScrapeResult(
                    success=False,
                    url=f"snapshot:{snapshot_id}",
                    status="timeout",
                    error=f"Polling timeout after {timeout}s",
                    snapshot_id=snapshot_id,
                    snapshot_polled_at=snapshot_polled_at
                )
            
            poll_time = datetime.utcnow()
            snapshot_polled_at.append(poll_time)
            
            status = await self.get_status(snapshot_id)
            
            if status == "ready":
                result = await self.fetch_result(snapshot_id)
                result.snapshot_polled_at = snapshot_polled_at
                return result
            elif status in ("error", "failed"):
                return ScrapeResult(
                    success=False,
                    url=f"snapshot:{snapshot_id}",
                    status="error",
                    error="Job failed",
                    snapshot_id=snapshot_id,
                    snapshot_polled_at=snapshot_polled_at
                )
            
            await asyncio.sleep(poll_interval)
```

#### 2.2 Sync Wrapper
```python
# src/brightdata/core/sync_wrapper.py
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar('T')

def run_sync(coro: Callable[..., Any]) -> Any:
    """
    Run async function in sync context.
    Handles both inside and outside event loop.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running - safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # Inside event loop - use thread pool
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
```

---

### PHASE 3: API Implementations (Week 3-4)

#### 3.1 Base API Class
```python
# src/brightdata/api/base.py
from abc import ABC, abstractmethod
from typing import Optional
from ..core.engine import AsyncEngine

class BaseAPI(ABC):
    """Base class for all API implementations."""
    
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
    
    @abstractmethod
    async def _execute_async(self, *args, **kwargs):
        """Execute API operation asynchronously."""
        pass
    
    def _execute_sync(self, *args, **kwargs):
        """Execute API operation synchronously."""
        from ..core.sync_wrapper import run_sync
        return run_sync(self._execute_async(*args, **kwargs))
```

#### 3.2 Web Unlocker API
```python
# src/brightdata/api/web_unlocker.py
from typing import Union, List
from .base import BaseAPI
from ..models import ScrapeResult
from ..utils.validation import validate_url

class WebUnlockerAPI(BaseAPI):
    """Web Unlocker API implementation."""
    
    async def scrape_async(
        self,
        url: Union[str, List[str]],
        zone: str,
        country: str = "",
        response_format: str = "raw",
        timeout: Optional[int] = None
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) asynchronously."""
        if isinstance(url, list):
            tasks = [self._scrape_single_async(u, zone, country, response_format, timeout) 
                     for u in url]
            return await asyncio.gather(*tasks)
        else:
            return await self._scrape_single_async(url, zone, country, response_format, timeout)
    
    async def _scrape_single_async(
        self,
        url: str,
        zone: str,
        country: str,
        response_format: str,
        timeout: Optional[int]
    ) -> ScrapeResult:
        """Scrape a single URL."""
        validate_url(url)
        
        # Implementation
        # ...
    
    def scrape(self, *args, **kwargs):
        """Scrape URL(s) synchronously."""
        return self._execute_sync(*args, **kwargs)
```

---

### PHASE 4: Registry Pattern (Week 4-5)

#### 4.1 Registry Implementation
```python
# src/brightdata/scrapers/registry.py
from typing import Dict, Type, Optional
from functools import lru_cache
import importlib
import pkgutil
import tldextract

_REGISTRY: Dict[str, Type] = {}

def register(domain: str):
    """Decorator to register a scraper for a domain."""
    def decorator(cls: Type) -> Type:
        _REGISTRY[domain.lower()] = cls
        return cls
    return decorator

@lru_cache(maxsize=1)
def _import_all_scrapers():
    """Import all scraper modules to trigger registration."""
    import brightdata.scrapers as pkg
    for mod in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if mod.name.endswith(".scraper"):
            importlib.import_module(mod.name)

def get_scraper_for(url: str) -> Optional[Type]:
    """Get scraper class for a URL."""
    _import_all_scrapers()
    extracted = tldextract.extract(url)
    domain = extracted.domain.lower()
    return _REGISTRY.get(domain)
```

#### 4.2 Base Scraper Class
```python
# src/brightdata/scrapers/base.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..core.engine import AsyncEngine
from ..models import ScrapeResult

class BaseScraper(ABC):
    """Base class for all specialized scrapers."""
    
    # Class attributes
    DATASET_ID: str = ""
    MIN_POLL_TIMEOUT: int = 180
    COST_PER_RECORD: float = 0.001
    
    def __init__(self, bearer_token: Optional[str] = None):
        import os
        token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
        if not token:
            raise ValueError("Bearer token required")
        self.engine = AsyncEngine(token)
    
    @abstractmethod
    async def collect_by_url_async(self, url: str) -> ScrapeResult:
        """Collect data from a specific URL asynchronously."""
        pass
    
    def collect_by_url(self, url: str) -> ScrapeResult:
        """Collect data from a specific URL synchronously."""
        from ..core.sync_wrapper import run_sync
        return run_sync(self.collect_by_url_async(url))
    
    async def poll_until_ready_async(
        self,
        snapshot_id: str,
        poll_interval: int = 10,
        timeout: int = 600
    ) -> ScrapeResult:
        """Poll until snapshot is ready."""
        async with self.engine as eng:
            return await eng.poll_until_ready(snapshot_id, poll_interval, timeout)
    
    def poll_until_ready(self, snapshot_id: str, **kwargs) -> ScrapeResult:
        """Poll until snapshot is ready (sync)."""
        from ..core.sync_wrapper import run_sync
        return run_sync(self.poll_until_ready_async(snapshot_id, **kwargs))
```

#### 4.3 Example Specialized Scraper
```python
# src/brightdata/scrapers/amazon/scraper.py
from typing import Optional
from ..base import BaseScraper
from ..registry import register
from ...models import ScrapeResult

@register("amazon")
class AmazonScraper(BaseScraper):
    """Amazon product scraper."""
    
    DATASET_ID = "gd_l7q7dkf244hwxbl93"  # Amazon Products
    MIN_POLL_TIMEOUT = 240
    
    async def collect_by_url_async(self, url: str) -> ScrapeResult:
        """Collect Amazon product data."""
        async with self.engine as eng:
            snapshot_id = await eng.trigger(
                payload=[{"url": url}],
                dataset_id=self.DATASET_ID
            )
            
            if not snapshot_id:
                return ScrapeResult(
                    success=False,
                    url=url,
                    status="error",
                    error="Failed to trigger collection"
                )
            
            return await eng.poll_until_ready(snapshot_id, timeout=self.MIN_POLL_TIMEOUT)
```

---

### PHASE 5: Simplified Auto API (Week 5-6)

#### 5.1 Auto Functions
```python
# src/brightdata/auto.py
"""Simplified one-liner API for common use cases."""

import os
from typing import Optional, List, Dict, Union
from .models import ScrapeResult
from .scrapers.registry import get_scraper_for
from .api.browser.browser_api import BrowserAPI

async def scrape_url_async(
    url: str,
    bearer_token: Optional[str] = None,
    fallback_to_browser: bool = True,
    poll_interval: int = 10,
    poll_timeout: int = 180
) -> Optional[ScrapeResult]:
    """
    Scrape a URL with automatic scraper detection.
    
    This is the simplest way to scrape a URL. The function will:
    1. Detect the domain automatically
    2. Use specialized scraper if available
    3. Fall back to Browser API if no specialized scraper
    
    Args:
        url: The URL to scrape
        bearer_token: Your Bright Data API token (or set BRIGHTDATA_TOKEN env var)
        fallback_to_browser: If True, use Browser API when no specialized scraper
        poll_interval: Seconds between status checks
        poll_timeout: Maximum seconds to wait for result
    
    Returns:
        ScrapeResult object with the data
    
    Example:
        >>> result = await scrape_url_async("https://www.amazon.com/dp/B0CRMZHDG8")
        >>> print(result.data)
    """
    token = bearer_token or os.getenv("BRIGHTDATA_TOKEN")
    if not token:
        raise ValueError("Bearer token required. Set BRIGHTDATA_TOKEN or pass bearer_token")
    
    # Try specialized scraper
    ScraperClass = get_scraper_for(url)
    if ScraperClass:
        scraper = ScraperClass(bearer_token=token)
        return await scraper.collect_by_url_async(url)
    
    # Fallback to Browser API
    if fallback_to_browser:
        browser_api = BrowserAPI()
        return await browser_api.fetch_async(url)
    
    return None

def scrape_url(url: str, **kwargs) -> Optional[ScrapeResult]:
    """
    Scrape a URL synchronously (blocks until complete).
    
    See scrape_url_async() for full documentation.
    
    Example:
        >>> result = scrape_url("https://www.amazon.com/dp/B0CRMZHDG8")
        >>> print(result.data)
    """
    from .core.sync_wrapper import run_sync
    return run_sync(scrape_url_async(url, **kwargs))

async def scrape_urls_async(
    urls: List[str],
    bearer_token: Optional[str] = None,
    fallback_to_browser: bool = True,
    max_concurrent: int = 10
) -> Dict[str, Optional[ScrapeResult]]:
    """
    Scrape multiple URLs concurrently.
    
    Args:
        urls: List of URLs to scrape
        bearer_token: API token
        fallback_to_browser: Use Browser API for unknown domains
        max_concurrent: Maximum concurrent operations
    
    Returns:
        Dict mapping URL to ScrapeResult
    """
    import asyncio
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _scrape_with_limit(url: str) -> tuple[str, Optional[ScrapeResult]]:
        async with semaphore:
            result = await scrape_url_async(url, bearer_token, fallback_to_browser)
            return url, result
    
    tasks = [_scrape_with_limit(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    return dict(results)

def scrape_urls(urls: List[str], **kwargs) -> Dict[str, Optional[ScrapeResult]]:
    """Scrape multiple URLs synchronously."""
    from .core.sync_wrapper import run_sync
    return run_sync(scrape_urls_async(urls, **kwargs))
```

---

### PHASE 6: Main Client (Week 6-7)

#### 6.1 Main Client Implementation
```python
# src/brightdata/client.py
"""Main Bright Data SDK client."""

import os
from typing import Optional, Union, List, Dict, Any
from .core.engine import AsyncEngine
from .core.zone_manager import ZoneManager
from .api.web_unlocker import WebUnlockerAPI
from .api.serp import SerpAPI
from .api.crawl import CrawlAPI
from .api.browser.browser_api import BrowserConnector
from .api.datasets import DatasetsAPI
from .models import ScrapeResult, CrawlResult
from .exceptions import ValidationError

class BrightData:
    """
    Modern async-first Bright Data SDK client.
    
    Example:
        >>> # Simple usage
        >>> client = BrightData(api_token="your_token")
        >>> result = client.scrape("https://example.com")
        >>> 
        >>> # Async usage
        >>> async with BrightData(api_token="your_token") as client:
        ...     result = await client.scrape_async("https://example.com")
    """
    
    DEFAULT_TIMEOUT = 30  # Aligned with docs
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        auto_create_zones: bool = True,
        web_unlocker_zone: str = "sdk_unlocker",
        serp_zone: str = "sdk_serp",
        browser_zone: str = "sdk_browser",
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize Bright Data client.
        
        Args:
            api_token: Your Bright Data API token (or set BRIGHTDATA_API_TOKEN)
            auto_create_zones: Automatically create zones if missing
            web_unlocker_zone: Zone name for web unlocker
            serp_zone: Zone name for SERP API
            browser_zone: Zone name for browser API
            timeout: Default timeout in seconds
        """
        self.api_token = api_token or os.getenv("BRIGHTDATA_API_TOKEN")
        if not self.api_token:
            raise ValidationError("API token required")
        
        self.web_unlocker_zone = web_unlocker_zone
        self.serp_zone = serp_zone
        self.browser_zone = browser_zone
        self.timeout = timeout
        
        # Initialize engine and APIs
        self.engine = AsyncEngine(self.api_token, timeout=timeout)
        self._zone_manager = ZoneManager(self.engine)
        
        # Initialize API implementations
        self._web_unlocker_api = WebUnlockerAPI(self.engine)
        self._serp_api = SerpAPI(self.engine)
        self._crawl_api = CrawlAPI(self.engine)
        self._browser_connector = BrowserConnector()
        self._datasets_api = DatasetsAPI(self.engine)
        
        # Auto-create zones if requested
        if auto_create_zones:
            self._ensure_zones()
    
    def _ensure_zones(self):
        """Ensure required zones exist."""
        from .core.sync_wrapper import run_sync
        run_sync(self._zone_manager.ensure_zones_async(
            self.web_unlocker_zone,
            self.serp_zone
        ))
    
    # ========== SCRAPING ==========
    
    async def scrape_async(
        self,
        url: Union[str, List[str]],
        zone: Optional[str] = None,
        country: str = "",
        response_format: str = "raw"
    ) -> Union[ScrapeResult, List[ScrapeResult]]:
        """Scrape URL(s) asynchronously using Web Unlocker API."""
        zone = zone or self.web_unlocker_zone
        return await self._web_unlocker_api.scrape_async(url, zone, country, response_format)
    
    def scrape(self, *args, **kwargs):
        """Scrape URL(s) synchronously."""
        from .core.sync_wrapper import run_sync
        return run_sync(self.scrape_async(*args, **kwargs))
    
    # ========== SEARCH ==========
    
    async def search_async(
        self,
        query: Union[str, List[str]],
        search_engine: str = "google",
        zone: Optional[str] = None,
        country: str = "us"
    ):
        """Perform web search asynchronously."""
        zone = zone or self.serp_zone
        return await self._serp_api.search_async(query, search_engine, zone, country)
    
    def search(self, *args, **kwargs):
        """Perform web search synchronously."""
        from .core.sync_wrapper import run_sync
        return run_sync(self.search_async(*args, **kwargs))
    
    # ========== CRAWLING ==========
    
    async def crawl_async(
        self,
        url: Union[str, List[str]],
        depth: Optional[int] = None,
        filter_pattern: str = "",
        exclude_pattern: str = ""
    ) -> CrawlResult:
        """Crawl website asynchronously."""
        return await self._crawl_api.crawl_async(url, depth, filter_pattern, exclude_pattern)
    
    def crawl(self, *args, **kwargs) -> CrawlResult:
        """Crawl website synchronously."""
        from .core.sync_wrapper import run_sync
        return run_sync(self.crawl_async(*args, **kwargs))
    
    # ========== BROWSER ==========
    
    def connect_browser(
        self,
        browser_username: Optional[str] = None,
        browser_password: Optional[str] = None,
        browser_type: str = "playwright"
    ) -> str:
        """
        Get WebSocket endpoint URL for browser automation.
        
        WARNING: The returned URL contains credentials. Do not log or expose it.
        """
        username = browser_username or os.getenv("BRIGHTDATA_BROWSER_USERNAME")
        password = browser_password or os.getenv("BRIGHTDATA_BROWSER_PASSWORD")
        
        if not username or not password:
            raise ValidationError("Browser credentials required")
        
        return self._browser_connector.get_endpoint(username, password, browser_type)
    
    # ========== DATASETS ==========
    
    async def download_snapshot_async(
        self,
        snapshot_id: str,
        format: str = "json"
    ):
        """Download snapshot data asynchronously."""
        return await self._datasets_api.download_snapshot_async(snapshot_id, format)
    
    def download_snapshot(self, *args, **kwargs):
        """Download snapshot data synchronously."""
        from .core.sync_wrapper import run_sync
        return run_sync(self.download_snapshot_async(*args, **kwargs))
    
    # ========== CONTEXT MANAGER ==========
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.engine.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.engine.__aexit__(exc_type, exc_val, exc_tb)
```

---

### PHASE 7: Testing Strategy (Week 7-8)

#### 7.1 Test Structure
```python
# tests/conftest.py
import pytest
import os
from brightdata import BrightData

@pytest.fixture
def api_token():
    """Get API token from environment."""
    token = os.getenv("BRIGHTDATA_API_TOKEN_TEST")
    if not token:
        pytest.skip("BRIGHTDATA_API_TOKEN_TEST not set")
    return token

@pytest.fixture
def client(api_token):
    """Create client instance."""
    return BrightData(api_token=api_token, auto_create_zones=False)

@pytest.fixture
async def async_client(api_token):
    """Create async client instance."""
    async with BrightData(api_token=api_token) as client:
        yield client

# tests/unit/test_models.py
def test_scrape_result_creation():
    """Test ScrapeResult creation."""
    from brightdata.models import ScrapeResult
    
    result = ScrapeResult(
        success=True,
        url="https://example.com",
        status="ready",
        data={"key": "value"}
    )
    
    assert result.success
    assert result.url == "https://example.com"
    assert result.data["key"] == "value"

# tests/integration/test_web_unlocker_api.py
@pytest.mark.asyncio
async def test_scrape_single_url(async_client):
    """Test scraping a single URL."""
    result = await async_client.scrape_async("https://httpbin.org/html")
    assert result.success
    assert result.data is not None

@pytest.mark.asyncio
async def test_scrape_multiple_urls(async_client):
    """Test scraping multiple URLs concurrently."""
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    results = await async_client.scrape_async(urls)
    assert len(results) == 2
    assert all(r.success for r in results)
```

#### 7.2 Test Coverage Goals
- Unit tests: 90%+ coverage
- Integration tests: All API endpoints
- E2E tests: Complete workflows
- Performance tests: Async vs sync comparison
- Load tests: 1000+ concurrent operations

---

### PHASE 8: Documentation (Week 8-9)

#### 8.1 Documentation Structure
```markdown
# Comprehensive Documentation

## Quick Start
- Installation
- Basic usage examples
- Authentication

## Core Concepts
- Async vs Sync
- Result objects
- Error handling
- Timeouts and retries

## API Reference
- BrightData client
- Auto functions
- Specialized scrapers
- Models and types

## Advanced Topics
- Custom scrapers
- Registry pattern
- Connection pooling
- Performance optimization

## Migration Guide
- From v1.x to v2.x
- Breaking changes
- Compatibility notes

## Contributing
- Development setup
- Code style
- Testing guidelines
- Release process
```

---

## CRITICAL IMPROVEMENTS OVER OLD-SDK

### 1. ARCHITECTURE ✅
**Old**: Monolithic client.py (897 lines)  
**New**: Modular structure with clear separation of concerns

### 2. ASYNC-FIRST ✅
**Old**: ThreadPoolExecutor (waterfall pattern)  
**New**: Native asyncio + aiohttp with sync wrappers

### 3. REGISTRY PATTERN ✅
**Old**: Hardcoded scraper mapping  
**New**: `@register()` decorator for auto-discovery

### 4. RESULT OBJECTS ✅
**Old**: Returns raw dict/str  
**New**: Rich `ScrapeResult` with timing, cost, methods

### 5. TIMEOUTS ✅
**Old**: DEFAULT_TIMEOUT = 65 (inconsistent)  
**New**: DEFAULT_TIMEOUT = 30 (aligned with docs)

### 6. ERROR HANDLING ✅
**Old**: Basic exception hierarchy  
**New**: Comprehensive exception classes with context

### 7. TYPE SAFETY ✅
**Old**: Minimal type hints  
**New**: Full type hints + protocols

### 8. TESTING ✅
**Old**: Minimal test coverage  
**New**: 90%+ coverage with unit/integration/e2e tests

### 9. DEVELOPER EXPERIENCE ✅
**Old**: Complex API, steep learning curve  
**New**: Simple `scrape_url()` + advanced options

### 10. PERFORMANCE ✅
**Old**: Sequential processing with threads  
**New**: True concurrency with asyncio

---

## ESTIMATED METRICS

### Performance Improvements
- **Async operations**: 10-50x faster for batch scraping
- **Memory usage**: 30-50% reduction through streaming
- **Connection overhead**: 70% reduction through connection pooling

### Code Quality
- **Lines of code**: ~3000 (down from ~4000 in old-sdk)
- **Cyclomatic complexity**: <10 per function
- **Test coverage**: 90%+
- **Type hint coverage**: 100%

### Developer Experience
- **Time to first scrape**: <5 minutes
- **API surface simplification**: Simple API for 80% of use cases
- **Documentation completeness**: 100% of public APIs

---

## DEPENDENCIES

### Runtime (Minimal)
```txt
aiohttp>=3.9.0           # Async HTTP client
requests>=2.31.0          # Sync HTTP client (backward compat)
python-dotenv>=1.0.0      # Environment variables
tldextract>=5.0.0         # Domain extraction for registry
pydantic>=2.0.0           # Data validation and settings
pydantic-settings>=2.0.0  # Environment variable support for config
```

### Development
```txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
```

### Optional
```txt
playwright>=1.40.0        # Browser automation
beautifulsoup4>=4.12.0    # HTML parsing
lxml>=4.9.0               # Fast XML/HTML parsing
```

---

## MIGRATION PATH FROM V1 TO V2

### Breaking Changes
1. Minimum Python version: 3.9+ (was 3.7+)
2. `bdclient` → `BrightData` (class rename)
3. Returns `ScrapeResult` objects instead of raw dict/str
4. Async methods require `await`

### Compatibility Layer
Provide v1 compatibility shim:
```python
# src/brightdata/compat/v1.py
from ..client import BrightData

class bdclient(BrightData):
    """Backward compatibility wrapper for v1.x API."""
    
    def scrape(self, *args, **kwargs):
        result = super().scrape(*args, **kwargs)
        # Convert ScrapeResult back to old format
        return result.data if result.success else None
```

---

## SUCCESS METRICS

### Adoption
- [ ] PyPI downloads: 10k+/month
- [ ] GitHub stars: 500+
- [ ] Documentation views: 5k+/month

### Quality
- [ ] Test coverage: 90%+
- [ ] Type hint coverage: 100%
- [ ] Code quality grade: A+
- [ ] Documentation completeness: 100%

### Performance
- [ ] Async 10x faster than sync for batch operations
- [ ] Memory usage 50% lower than v1
- [ ] Zero memory leaks under load testing

### Community
- [ ] 10+ external contributors
- [ ] 95%+ positive feedback
- [ ] Active community support

---

## TIMELINE SUMMARY

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Foundation | 1-2 weeks | Project setup, models, exceptions |
| 2. Core Engine | 1 week | Async HTTP engine, sync wrappers |
| 3. API Layer | 1 week | All API implementations |
| 4. Registry | 1 week | Registry pattern + base scrapers |
| 5. Auto API | 1 week | Simplified scrape_url() functions |
| 6. Main Client | 1 week | Complete BrightData client |
| 7. Testing | 1 week | Comprehensive test suite |
| 8. Documentation | 1 week | Complete documentation |
| 9. Polish | 1 week | Performance tuning, bug fixes |
| **TOTAL** | **9 weeks** | **Production-ready v2.0.0** |

---

## CONCLUSION

This plan creates a **world-class Python SDK** that:

✅ Follows modern Python best practices  
✅ Provides both simple and advanced APIs  
✅ Achieves 10-50x performance improvements  
✅ Maintains backward compatibility options  
✅ Has comprehensive testing and documentation  
✅ Is extensible and maintainable  
✅ Matches FAANG-level engineering standards  

The new SDK will be a **reference implementation** for Python SDKs in the web scraping industry.
