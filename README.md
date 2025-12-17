# Bright Data Python SDK

The official Python SDK for [Bright Data](https://brightdata.com) APIs. Scrape any website, get SERP results, bypass bot detection and CAPTCHAs.

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

### Search Engines (SERP)

```python
async with BrightDataClient() as client:
    result = await client.search.google(query="python scraping", num_results=10)
    for item in result.data:
        print(item)
```

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
