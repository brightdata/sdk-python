# Bright Data Python SDK Changelog

## Version 2.1.0 - API Simplification & Naming Convention Fix

### 🚨 Breaking Changes

#### Removed GenericScraper
```python
# OLD (v2.0.0)
result = await client.scrape.generic.url("https://example.com")

# NEW (v2.1.0) - Use scrape_url() directly
result = await client.scrape_url("https://example.com")
```

#### Async Method Naming Convention
The `_async` suffix has been removed. Now `method()` is async by default, and `method_sync()` is the synchronous version.

```python
# OLD (v2.0.0)
result = await scraper.products_async(url)
await job.wait_async()
data = await job.fetch_async()

# NEW (v2.1.0)
result = await scraper.products(url)
await job.wait()
data = await job.fetch()
```

#### CLI Command Change
```bash
# OLD
brightdata scrape generic --url https://example.com

# NEW
brightdata scrape url --url https://example.com
```

### ✨ New Features

#### Complete SyncBrightDataClient
Added comprehensive `sync_client.py` with full coverage for all scrapers:

```python
from brightdata import SyncBrightDataClient

with SyncBrightDataClient(token="...") as client:
    # All methods work synchronously
    result = client.scrape.amazon.products(url)
    result = client.scrape.linkedin.profiles(url)
    result = client.search.google("query")
```

**Supported sync wrappers:**
- `SyncAmazonScraper` - products, reviews, sellers (+ trigger/status/fetch)
- `SyncLinkedInScraper` - profiles, jobs, companies, posts
- `SyncInstagramScraper` - profiles, posts, comments, reels
- `SyncFacebookScraper` - posts_by_profile, posts_by_group, comments, reels
- `SyncChatGPTScraper` - prompt, prompts
- `SyncSearchService` - google, bing, yandex
- `SyncCrawlerService` - crawl, scrape

#### Context Manager Enforcement
Client methods now require proper context manager initialization:

```python
# Correct usage
async with BrightDataClient() as client:
    result = await client.scrape_url(url)

# Will raise RuntimeError
client = BrightDataClient()
result = await client.scrape_url(url)  # Error: not initialized
```

### 🔄 Migration Guide

#### Method Renames
| Old (v2.0.0) | New (v2.1.0) |
|--------------|--------------|
| `products_async()` | `products()` |
| `reviews_async()` | `reviews()` |
| `profiles_async()` | `profiles()` |
| `jobs_async()` | `jobs()` |
| `wait_async()` | `wait()` |
| `fetch_async()` | `fetch()` |
| `to_result_async()` | `to_result()` |
| `status_async()` | `status()` |
| `scrape.generic.url()` | `scrape_url()` |

#### Quick Migration
```bash
# Find and replace in your codebase:
_async() → ()
scrape.generic.url → scrape_url
```

### 📝 Documentation
- Simplified README with clearer examples
- Updated all examples and tests to use new naming convention

---

## Version 2.0.0 - Complete Architecture Rewrite

### 🚨 Breaking Changes

#### Client Initialization
```python
# OLD (v1.1.3)
from brightdata import bdclient
client = bdclient(api_token="your_token")

# NEW (v2.0.0)
from brightdata import BrightDataClient
client = BrightDataClient(token="your_token")
```

#### API Structure Changes
- **Old**: Flat API with methods directly on client (`client.scrape()`, `client.search()`)
- **New**: Hierarchical service-based API (`client.scrape.amazon.products()`, `client.search.google()`)

#### Method Naming Convention
```python
# OLD
client.scrape_linkedin.profiles(url)
client.search_linkedin.jobs()

# NEW
client.scrape.linkedin.profiles(url)
client.search.linkedin.jobs()
```

#### Return Types
- **Old**: Raw dictionaries and strings
- **New**: Structured `ScrapeResult` and `SearchResult` objects with metadata and timing metrics

#### Python Version Requirement
- **Old**: Python 3.8+
- **New**: Python 3.9+ (dropped Python 3.8 support)

### 🎯 Major Architectural Changes

#### 1. Async-First Architecture
**Old**: Synchronous with `ThreadPoolExecutor` for concurrency
```python
# Old approach - thread-based parallelism
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(self.scrape, urls)
```

**New**: Native async/await throughout with sync wrappers
```python
# New approach - native async (method() is async by default)
async def products(self, url):
    async with self.engine:
        return await self._execute_workflow(...)

# Sync client uses persistent event loop
with SyncBrightDataClient() as client:
    result = client.scrape.amazon.products(url)
```

#### 2. Service-Based Architecture
**Old**: Monolithic `bdclient` class with all methods
**New**: Layered architecture with specialized services
```
BrightDataClient
├── scrape (ScrapeService)
│   ├── amazon (AmazonScraper)
│   ├── linkedin (LinkedInScraper)
│   └── instagram (InstagramScraper)
├── search (SearchService)
│   ├── google
│   ├── bing
│   └── yandex
└── crawler (CrawlService)
```

#### 3. Workflow Pattern Implementation
**Old**: Direct HTTP requests with immediate responses
**New**: Trigger/Poll/Fetch workflow for long-running operations
```python
# New workflow pattern
snapshot_id = await trigger(payload)     # Start job
status = await poll_until_ready(snapshot_id)  # Check progress
data = await fetch_results(snapshot_id)  # Get results
```

### ✨ New Features

#### 1. Comprehensive Platform Support
| Platform | Old SDK | New SDK | New Capabilities |
|----------|---------|---------|------------------|
| Amazon | ❌ | ✅ | Products, Reviews, Sellers (separate datasets) |
| LinkedIn | ✅ Basic | ✅ Full | Enhanced scraping and search methods |
| Instagram | ❌ | ✅ | Profiles, Posts, Comments, Reels |
| Facebook | ❌ | ✅ | Posts, Comments, Groups |
| ChatGPT | ✅ Basic | ✅ Enhanced | Improved prompt interaction |
| Google Search | ✅ | ✅ Enhanced | Dedicated service with better structure |
| Bing/Yandex | ✅ | ✅ Enhanced | Separate service methods |

#### 2. Manual Job Control
```python
# New capability - fine-grained control over scraping jobs
job = await scraper.products_trigger(url)
# Do other work...
status = await job.status()
if status == "ready":
    data = await job.fetch()
```

#### 3. Type-Safe Payloads (Dataclasses)
```python
# New - structured payloads with validation
from brightdata import AmazonProductPayload
payload = AmazonProductPayload(
    url="https://amazon.com/dp/B123",
    reviews_count=100
)

# Old - untyped dictionaries
payload = {"url": "...", "reviews_count": 100}
```

#### 4. CLI Tool
```bash
# New - command-line interface
brightdata scrape amazon products --url https://amazon.com/dp/B123
brightdata search google --query "python sdk"
brightdata crawler discover --url https://example.com --depth 3

# Old - no CLI support
```

#### 5. Registry Pattern for Scrapers
```python
# New - self-registering scrapers
@register("amazon")
class AmazonScraper(BaseWebScraper):
    DATASET_ID = "gd_l7q7dkf244hwxbl93"
```

#### 6. Advanced Telemetry
- SDK function tracking via stack inspection
- Microsecond-precision timestamps for all operations
- Comprehensive cost tracking per platform
- Detailed timing metrics in results

### 🚀 Performance Improvements

#### Connection Management
- **Old**: New connection per request, basic session management
- **New**: Advanced connection pooling (100 total, 30 per host) with keep-alive

#### Concurrency Model
- **Old**: Thread-based with GIL limitations
- **New**: Event loop-based with true async concurrency

#### Resource Management
- **Old**: Basic cleanup with requests library
- **New**: Triple-layer cleanup strategy with context managers and idempotent operations

#### Rate Limiting
- **Old**: No built-in rate limiting
- **New**: Optional `AsyncLimiter` integration (10 req/sec default)

### 📦 Dependency Changes

#### Removed Dependencies
- `beautifulsoup4` - Parsing moved to server-side
- `openai` - Not needed for ChatGPT scraping

#### New Dependencies
- `tldextract` - Domain extraction for registry
- `pydantic` - Data validation (optional)
- `aiolimiter` - Rate limiting support
- `click` - CLI framework

#### Updated Dependencies
- `aiohttp>=3.8.0` - Core async HTTP client (was using requests for sync)

### 🔧 Configuration Changes

#### Environment Variables
```bash
# Supported in both old and new versions:
BRIGHTDATA_API_TOKEN=token
WEB_UNLOCKER_ZONE=zone
SERP_ZONE=zone
BROWSER_ZONE=zone
BRIGHTDATA_BROWSER_USERNAME=username
BRIGHTDATA_BROWSER_PASSWORD=password

# Note: Rate limiting is NOT configured via environment variable
# It must be set programmatically when creating the client
```

#### Client Parameters
```python
# Old (v1.1.3)
client = bdclient(
    api_token="token",                  # Required parameter name
    auto_create_zones=True,              # Default: True
    web_unlocker_zone="sdk_unlocker",   # Default from env or 'sdk_unlocker'
    serp_zone="sdk_serp",               # Default from env or 'sdk_serp'
    browser_zone="sdk_browser",         # Default from env or 'sdk_browser'
    browser_username="username",
    browser_password="password",
    browser_type="playwright",
    log_level="INFO",
    structured_logging=True,
    verbose=False
)

# New (v2.0.0)
client = BrightDataClient(
    token="token",                       # Changed parameter name (was api_token)
    customer_id="id",                    # New parameter (optional)
    timeout=30,                          # New parameter (default: 30)
    auto_create_zones=False,             # Changed default: now False (was True)
    web_unlocker_zone="web_unlocker1",  # Changed default name
    serp_zone="serp_api1",              # Changed default name
    browser_zone="browser_api1",        # Changed default name
    validate_token=False,                # New parameter
    rate_limit=10,                      # New parameter (optional)
    rate_period=1.0                     # New parameter (default: 1.0)
)
# Note: browser credentials and logging config removed from client init
```

### 🔄 Migration Guide

#### Basic Scraping
```python
# Old
result = client.scrape(url, zone="my_zone", response_format="json")

# New (minimal change)
result = client.scrape_url(url, zone="my_zone", response_format="json")

# New (recommended - platform-specific)
result = client.scrape.amazon.products(url)
```

#### LinkedIn Operations
```python
# Old
profiles = client.scrape_linkedin.profiles(url)
jobs = client.search_linkedin.jobs(location="Paris")

# New
profiles = client.scrape.linkedin.profiles(url)
jobs = client.search.linkedin.jobs(location="Paris")
```

#### Search Operations
```python
# Old
results = client.search(query, search_engine="google")

# New
results = client.search.google(query)
```

#### Async Migration
```python
# Old (sync only)
result = client.scrape(url)

# New (async-first)
async def main():
    async with BrightDataClient(token="...") as client:
        result = await client.scrape_url(url)

# Or use sync client
with SyncBrightDataClient(token="...") as client:
    result = client.scrape_url(url)
```


### 🎯 Summary

Version 2.0.0 represents a **complete rewrite** of the Bright Data Python SDK, not an incremental update. The new architecture prioritizes:

1. **Modern Python patterns**: Async-first with proper resource management
2. **Developer experience**: Hierarchical APIs, type safety, CLI tools
3. **Production reliability**: Comprehensive error handling, telemetry
4. **Platform coverage**: All major platforms with specialized scrapers
5. **Flexibility**: Three levels of control (simple, workflow, manual)

This is a **breaking release** requiring code changes. The migration effort is justified by:
- 10x improvement in concurrent operation handling
- 50+ new platform-specific methods
- Proper async support for modern applications
- Comprehensive timing and cost tracking
- Future-proof architecture for new platforms

### 📝 Upgrade Checklist

- [ ] Update Python to 3.9+
- [ ] Update import statements from `bdclient` to `BrightDataClient`
- [ ] Migrate to hierarchical API structure
- [ ] Update method calls to new naming convention
- [ ] Handle new `ScrapeResult`/`SearchResult` return types
- [ ] Consider async-first approach for better performance
- [ ] Review and update error handling for new exception types
- [ ] Test rate limiting configuration if needed
- [ ] Validate platform-specific scraper migrations