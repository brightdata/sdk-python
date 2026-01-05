# Sync Client

`SyncBrightDataClient` provides a synchronous interface for the Bright Data SDK. Use it when you don't need async/await or for simpler scripts.

## Basic Usage

```python
from brightdata import SyncBrightDataClient

with SyncBrightDataClient() as client:
    result = client.scrape_url("https://example.com")
    print(result.data)
```

## How It Works

- Wraps the async `BrightDataClient` with a persistent event loop
- All methods have the same signature as the async client (without `await`)
- Uses `run_until_complete()` internally for better performance than repeated `asyncio.run()` calls

## Available Methods

### Client Methods

```python
client.scrape_url(url, **kwargs)      # Scrape any URL
client.test_connection()               # Test API connection
client.get_account_info()              # Get account info
client.list_zones()                    # List all zones
client.delete_zone(zone_name)          # Delete a zone
```

### Scrape Service

```python
# Amazon
client.scrape.amazon.products(url)
client.scrape.amazon.products_trigger(url)
client.scrape.amazon.products_status(snapshot_id)
client.scrape.amazon.products_fetch(snapshot_id)
client.scrape.amazon.reviews(url)
client.scrape.amazon.sellers(url)

# LinkedIn
client.scrape.linkedin.profiles(url)
client.scrape.linkedin.companies(url)
client.scrape.linkedin.jobs(url)
client.scrape.linkedin.posts(url)

# Instagram
client.scrape.instagram.profiles(url)
client.scrape.instagram.posts(url)
client.scrape.instagram.comments(url)
client.scrape.instagram.reels(url)

# Facebook
client.scrape.facebook.posts_by_profile(url)
client.scrape.facebook.posts_by_group(url)
client.scrape.facebook.comments(url)
client.scrape.facebook.reels(url)

# ChatGPT
client.scrape.chatgpt.prompt(prompt)
client.scrape.chatgpt.prompts(prompts)
```

### Search Service

```python
client.search.google(query)
client.search.bing(query)
client.search.yandex(query)
client.search.amazon.products(keyword)
client.search.linkedin.jobs(keyword)
client.search.linkedin.profiles(**kwargs)
```

### Crawler Service

```python
client.crawler.crawl(url)
client.crawler.scrape(url)
```

## Important Notes

### Not Thread-Safe

`SyncBrightDataClient` is **not thread-safe**. For multi-threaded usage, create a separate client per thread:

```python
import threading

def worker():
    with SyncBrightDataClient() as client:
        result = client.scrape_url("https://example.com")

threads = [threading.Thread(target=worker) for _ in range(3)]
for t in threads:
    t.start()
```

### Cannot Use Inside Async Context

Using `SyncBrightDataClient` inside an async function will raise an error:

```python
# Wrong - will raise RuntimeError
async def main():
    with SyncBrightDataClient() as client:  # Error!
        ...

# Correct - use async client
async def main():
    async with BrightDataClient() as client:
        result = await client.scrape_url("...")
```

## When to Use Sync vs Async

| Use Case | Recommended |
|----------|-------------|
| Simple scripts | `SyncBrightDataClient` |
| Jupyter notebooks | `SyncBrightDataClient` |
| Web frameworks (FastAPI, etc.) | `BrightDataClient` (async) |
| High-volume scraping | `BrightDataClient` (async) |
| Concurrent requests | `BrightDataClient` (async) |
