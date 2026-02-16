# Bright Data Python SDK

The official Python SDK for [Bright Data](https://brightdata.com) APIs. Scrape any website, get SERP results, bypass bot detection and CAPTCHAs, and access 100+ ready-made datasets.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Installation

```bash
pip install brightdata-sdk
```

## Configuration

Get your API Token from the [Bright Data Control Panel](https://brightdata.com/cp/api_keys):

```bash
export BRIGHTDATA_API_TOKEN="your_api_token_here"
```

## Quick Start

This SDK is **async-native**. A sync client is also available (see [Sync Client](#sync-client)).

```python
import asyncio
from brightdata import BrightDataClient

async def main():
    async with BrightDataClient() as client:
        result = await client.scrape_url("https://example.com")
        print(result.data)

asyncio.run(main())
```

## Usage Examples

### Web Scraping

```python
async with BrightDataClient() as client:
    result = await client.scrape_url("https://example.com")
    print(result.data)
```

#### Web Scraping Async Mode

For non-blocking web scraping, use `mode="async"`. This triggers a request and returns a `response_id`, which the SDK automatically polls until results are ready:

```python
async with BrightDataClient() as client:
    # Triggers request → gets response_id → polls until ready
    result = await client.scrape_url(
        url="https://example.com",
        mode="async",
        poll_interval=5,    # Check every 5 seconds
        poll_timeout=180    # Web Unlocker async can take ~2 minutes
    )
    print(result.data)

    # Batch scraping multiple URLs concurrently
    urls = ["https://example.com", "https://example.org", "https://example.net"]
    results = await client.scrape_url(url=urls, mode="async", poll_timeout=180)
```

**How it works:**
1. Sends request to `/unblocker/req` → returns `response_id` immediately
2. Polls `/unblocker/get_result?response_id=...` until ready or timeout
3. Returns the scraped data

**When to use async mode:**
- Batch scraping with many URLs
- Background processing while continuing other work

**Performance note:** Web Unlocker async mode typically takes ~2 minutes to complete. For faster results on single URLs, use the default sync mode (no `mode` parameter).

### Search Engines (SERP)

```python
async with BrightDataClient() as client:
    result = await client.search.google(query="python scraping", num_results=10)
    for item in result.data:
        print(item)
```

#### SERP Async Mode

For non-blocking SERP requests, use `mode="async"`:

```python
async with BrightDataClient() as client:
    # Non-blocking - polls for results
    result = await client.search.google(
        query="python programming",
        mode="async",
        poll_interval=2,   # Check every 2 seconds
        poll_timeout=30    # Give up after 30 seconds
    )

    for item in result.data:
        print(item['title'], item['link'])
```

**When to use async mode:**
- Batch operations with many queries
- Background processing while continuing other work
- When scraping may take longer than usual

**Note:** Async mode uses the same zones and returns the same data structure as sync mode - no extra configuration needed!

### Web Scraper API

The SDK includes ready-to-use scrapers for popular websites: Amazon, LinkedIn, Instagram, Facebook, and more.

**Pattern:** `client.scrape.<platform>.<method>(url)`

**Example: Amazon**
```python
async with BrightDataClient() as client:
    # Product details
    result = await client.scrape.amazon.products(url="https://amazon.com/dp/B0CRMZHDG8")

    # Reviews
    result = await client.scrape.amazon.reviews(url="https://amazon.com/dp/B0CRMZHDG8")

    # Sellers
    result = await client.scrape.amazon.sellers(url="https://amazon.com/dp/B0CRMZHDG8")
```

**Available scrapers:**
- `client.scrape.amazon` - products, reviews, sellers
- `client.scrape.linkedin` - profiles, companies, jobs, posts
- `client.scrape.instagram` - profiles, posts, comments, reels
- `client.scrape.facebook` - posts, comments, reels

## Datasets API

Access 100+ ready-made datasets from Bright Data — pre-collected, structured data from popular platforms.

```python
async with BrightDataClient() as client:
    # Filter a dataset — returns a snapshot_id
    snapshot_id = await client.datasets.imdb_movies(
        filter={"name": "title", "operator": "includes", "value": "black"},
        records_limit=5
    )

    # Download when ready (polls until snapshot is complete)
    data = await client.datasets.imdb_movies.download(snapshot_id)
    print(f"Got {len(data)} records")

    # Quick sample: .sample() auto-discovers fields, no filter needed
    # Works on any dataset
    snapshot_id = await client.datasets.imdb_movies.sample(records_limit=5)
```

**Export results to file:**

```python
from brightdata.datasets import export

export(data, "results.json")   # JSON
export(data, "results.csv")    # CSV
export(data, "results.jsonl")  # JSONL
```

**Available dataset categories:**
- **E-commerce:** Amazon, Walmart, Shopee, Lazada, Zalando, Zara, H&M, Shein, IKEA, Sephora, and more
- **Business intelligence:** ZoomInfo, PitchBook, Owler, Slintel, VentureRadar, Manta
- **Jobs & HR:** Glassdoor (companies, reviews, jobs), Indeed (companies, jobs), Xing
- **Reviews:** Google Maps, Yelp, G2, Trustpilot, TrustRadius
- **Social media:** Pinterest (posts, profiles), Facebook Pages
- **Real estate:** Zillow, Airbnb, and 8+ regional platforms
- **Luxury brands:** Chanel, Dior, Prada, Balenciaga, Hermes, YSL, and more
- **Entertainment:** IMDB, NBA, Goodreads

**Discover available fields:**

```python
metadata = await client.datasets.imdb_movies.get_metadata()
for name, field in metadata.fields.items():
    print(f"{name}: {field.type}")
```

## Async Usage

Run multiple requests concurrently:

```python
import asyncio
from brightdata import BrightDataClient

async def main():
    async with BrightDataClient() as client:
        urls = ["https://example.com/page1", "https://example.com/page2", "https://example.com/page3"]
        tasks = [client.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

### Manual Trigger/Poll/Fetch

For long-running scrapes:

```python
async with BrightDataClient() as client:
    # Trigger
    job = await client.scrape.amazon.products_trigger(url="https://amazon.com/dp/B123")

    # Wait for completion
    await job.wait(timeout=180)

    # Fetch results
    data = await job.fetch()
```

## Sync Client

For simpler use cases, use `SyncBrightDataClient`:

```python
from brightdata import SyncBrightDataClient

with SyncBrightDataClient() as client:
    result = client.scrape_url("https://example.com")
    print(result.data)

    # All methods work the same
    result = client.scrape.amazon.products(url="https://amazon.com/dp/B123")
    result = client.search.google(query="python")
```

See [docs/sync_client.md](docs/sync_client.md) for details.

## Troubleshooting

**RuntimeError: SyncBrightDataClient cannot be used inside async context**
```python
# Wrong - using sync client in async function
async def main():
    with SyncBrightDataClient() as client:  # Error!
        ...

# Correct - use async client
async def main():
    async with BrightDataClient() as client:
        result = await client.scrape_url("https://example.com")
```

**RuntimeError: BrightDataClient not initialized**
```python
# Wrong - forgot context manager
client = BrightDataClient()
result = await client.scrape_url("...")  # Error!

# Correct - use context manager
async with BrightDataClient() as client:
    result = await client.scrape_url("...")
```

## License

MIT License
