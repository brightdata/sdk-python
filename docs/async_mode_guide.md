# Async Mode Guide

## Overview

Async mode allows non-blocking requests for both SERP and Web Unlocker APIs using Bright Data's unblocker endpoints. This enables batch operations, background processing, and better resource utilization.

This guide covers:
- **SERP Async Mode**: Non-blocking search engine scraping
- **Web Unlocker Async Mode**: Non-blocking web page scraping

## Sync vs Async Comparison

| Feature | Sync Mode (Default) | Async Mode |
|---------|-------------------|------------|
| Endpoint | `/request` | `/unblocker/req` + `/unblocker/get_result` |
| Behavior | Blocks until ready | Returns immediately, polls for results |
| Use Case | Simple queries | Batch operations, background tasks |
| Response | Normalized SERP data | Same normalized SERP data |
| Configuration | None (default) | `mode="async"` |
| customer_id | Not required | Not required |

## Key Benefits

1. **Non-Blocking**: Continue working while scraping happens in background
2. **Batch Processing**: Trigger multiple searches, collect results later
3. **Same Data Structure**: Both modes return identical normalized data
4. **No Extra Setup**: Works with existing zones and authentication

## Basic Usage

### Default (Sync Mode)

This is the existing behavior - backwards compatible:

```python
from brightdata import BrightDataClient

async with BrightDataClient() as client:
    result = await client.search.google(
        query="test",
        zone="my_serp_zone"
    )
    # Blocks until results ready, then returns
    print(result.data)
```

### Async Mode

Simply add `mode="async"`:

```python
from brightdata import BrightDataClient

async with BrightDataClient() as client:
    result = await client.search.google(
        query="test",
        zone="my_serp_zone",
        mode="async",        # ← Enable async mode
        poll_interval=2,     # Check every 2 seconds
        poll_timeout=30      # Give up after 30 seconds
    )
    # Triggers request, polls until ready or timeout
    print(result.data)
```

## Advanced Usage

### Batch Operations

Process multiple queries efficiently:

```python
async with BrightDataClient() as client:
    queries = ["python", "javascript", "golang"]

    # All queries triggered concurrently, each polled independently
    results = await client.search.google(
        query=queries,
        zone="my_zone",
        mode="async",
        poll_interval=2,
        poll_timeout=60  # Longer timeout for batch
    )

    for result in results:
        if result.success:
            print(f"Query: {result.query['q']}")
            print(f"Results: {len(result.data)}")
        else:
            print(f"Error: {result.error}")
```

### With Location Parameters

Async mode supports all the same parameters as sync:

```python
result = await client.search.google(
    query="restaurants",
    zone="my_zone",
    location="US",
    language="en",
    device="desktop",
    num_results=20,
    mode="async",
    poll_interval=2,
    poll_timeout=30
)
```

### Handling Timeouts

```python
result = await client.search.google(
    query="complex query",
    zone="my_zone",
    mode="async",
    poll_timeout=10  # Short timeout
)

if not result.success:
    if "timeout" in result.error.lower():
        print("Search timed out - try increasing poll_timeout")
    else:
        print(f"Error: {result.error}")
```

## Configuration

### No Extra Setup Required!

Unlike other async implementations, Bright Data's async unblocker:
- ✅ Doesn't require customer_id (derived from API token)
- ✅ Works with the same zones as sync mode
- ✅ Returns the same data structure
- ✅ Uses the same authentication

Just add `mode="async"` to any existing SERP call.

### Polling Parameters

Fine-tune polling behavior:

```python
result = await client.search.google(
    query="test",
    zone="my_zone",
    mode="async",
    poll_interval=5,   # Wait 5 seconds between checks (default: 2)
    poll_timeout=120   # Give up after 2 minutes (default: 30)
)
```

**Recommendations:**
- `poll_interval`: 2-5 seconds (balance between responsiveness and API load)
- `poll_timeout`: 30-60 seconds for single queries, 60-120 for batches

## Performance

### Trigger Time

- **Sync mode**: Blocks for entire scrape (~2-5 seconds)
- **Async mode**: Returns after trigger (~0.5-1 second)

### Total Time

Total time is similar for both modes - the difference is whether you **block** or **poll**:

```
Sync:  [====== WAIT ======] → Results
Async: [Trigger] ... [Poll] [Poll] [Poll] → Results
               ↑
          Do other work here!
```

### Batch Efficiency

Async mode shines for batches:

```python
# Sync mode: Sequential (~15 seconds for 5 queries)
for query in queries:
    result = await search(query, mode="sync")  # 3s each

# Async mode: Concurrent (~3-5 seconds for 5 queries)
results = await search(queries, mode="async")  # All triggered at once
```

## Error Handling

Async mode returns the same `SearchResult` structure with error handling:

```python
result = await client.search.google(
    query="test",
    zone="my_zone",
    mode="async",
    poll_timeout=10
)

if result.success:
    print(f"Got {len(result.data)} results")
else:
    print(f"Error: {result.error}")
    # Common errors:
    # - "Polling timeout after 10s (response_id: ...)"
    # - "Async request failed (response_id: ...)"
    # - "Failed to trigger async request (no response_id received)"
```

## Migration Guide

### From Sync to Async

**Before (Sync):**
```python
result = await client.search.google(query="test", zone="my_zone")
```

**After (Async):**
```python
result = await client.search.google(
    query="test",
    zone="my_zone",
    mode="async",
    poll_interval=2,
    poll_timeout=30
)
```

### No Breaking Changes

Existing code continues to work without modification:

```python
# This still works exactly as before (defaults to sync mode)
result = await client.search.google(query="test", zone="my_zone")
```

## Supported Search Engines

Async mode works with all SERP endpoints:

- ✅ Google: `client.search.google()`
- ✅ Bing: `client.search.bing()`
- ✅ Yandex: `client.search.yandex()`

All support the same `mode="async"` parameter.

## Technical Details

### How It Works

1. **Trigger**: POST to `/unblocker/req?zone=X` with search URL
2. **Response ID**: Receive `x-response-id` header
3. **Poll**: GET `/unblocker/get_result?zone=X&response_id=Y`
   - HTTP 202: Still pending, wait and retry
   - HTTP 200: Results ready, fetch data
   - Other: Error occurred
4. **Results**: Parse and normalize SERP data

### Response Structure

Both sync and async return the same normalized structure:

```python
{
    "general": {
        "search_engine": "google",
        "query": "python programming",
        "language": "en-US"
    },
    "organic": [
        {
            "rank": 1,
            "title": "Welcome to Python.org",
            "link": "https://www.python.org/",
            "description": "..."
        }
    ],
    "top_ads": [...],
    "knowledge": {...}
}
```

## Best Practices

1. **Use async for batches**: If processing >3 queries, async mode is more efficient
2. **Set reasonable timeouts**: Give enough time but don't wait forever
3. **Handle errors gracefully**: Check `result.success` before accessing data
4. **Monitor poll_interval**: Don't poll too aggressively (2-5s is good)
5. **Stick with sync for one-offs**: For single, simple queries, sync is simpler

## Troubleshooting

### "Polling timeout after 30s"

**Cause**: Search took longer than `poll_timeout`

**Solution**: Increase `poll_timeout` or check if query is too complex

### "Failed to trigger async request"

**Cause**: Trigger endpoint didn't return response_id

**Solution**: Check zone configuration, API token validity

### "Response not ready yet (HTTP 202)"

**Cause**: Called fetch before results ready (shouldn't happen with polling)

**Solution**: This is handled internally - if you see this, it's a bug

## FAQ

**Q: Do I need customer_id for async mode?**

A: No! Unlike other implementations, Bright Data derives customer from your API token.

**Q: Will async mode cost more?**

A: No, costs are the same for both modes.

**Q: Can I use async mode with custom zones?**

A: Yes, async mode works with any zone that supports SERP.

**Q: What's the difference between this and asyncio?**

A: This is about Bright Data's API behavior (blocking vs polling), not Python's async/await. The SDK is already asyncio-based.

**Q: Can I mix sync and async in the same code?**

A: Yes! Choose mode per request:

```python
result1 = await search(query1, mode="sync")   # Blocking
result2 = await search(query2, mode="async")  # Non-blocking
```

---

# Web Unlocker Async Mode

## Overview

Web Unlocker also supports async mode using the same unblocker endpoints. This enables non-blocking HTML scraping for better batch processing and resource utilization.

## Sync vs Async for Web Unlocker

| Feature | Sync Mode (Default) | Async Mode |
|---------|-------------------|------------|
| Endpoint | `/request` | `/unblocker/req` + `/unblocker/get_result` |
| Behavior | Blocks until ready | Returns immediately, polls for results |
| Use Case | Single page scrapes | Batch scraping, background tasks |
| Response | HTML/JSON | Same HTML/JSON |
| Configuration | None (default) | `mode="async"` |

## Basic Usage

### Default (Sync Mode)

Existing behavior - backwards compatible:

```python
from brightdata import BrightDataClient

async with BrightDataClient() as client:
    result = await client.scrape_url(
        url="https://example.com",
        zone="my_web_unlocker_zone"
    )
    # Blocks until scraping complete
    print(result.data)  # HTML content
```

### Async Mode

Simply add `mode="async"`:

```python
from brightdata import BrightDataClient

async with BrightDataClient() as client:
    result = await client.scrape_url(
        url="https://example.com",
        zone="my_web_unlocker_zone",
        mode="async",        # ← Enable async mode
        poll_interval=2,     # Check every 2 seconds
        poll_timeout=30      # Give up after 30 seconds
    )
    # Triggers request, polls until ready or timeout
    print(result.data)  # HTML content
```

## Advanced Usage

### Batch URL Scraping

Process multiple URLs efficiently:

```python
async with BrightDataClient() as client:
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]

    # All URLs triggered concurrently, each polled independently
    results = await client.scrape_url(
        url=urls,
        zone="my_zone",
        mode="async",
        poll_interval=2,
        poll_timeout=60  # Longer timeout for batch
    )

    for i, result in enumerate(results):
        if result.success:
            print(f"URL {i+1}: {len(result.data)} bytes")
        else:
            print(f"URL {i+1} failed: {result.error}")
```

### With Country and Response Format

Async mode supports all the same parameters as sync:

```python
result = await client.scrape_url(
    url="https://api.example.com/data",
    zone="my_zone",
    country="US",
    response_format="json",  # Get JSON instead of raw HTML
    mode="async",
    poll_interval=2,
    poll_timeout=30
)

if result.success:
    print(result.data)  # Parsed JSON dict
```

### Handling Timeouts

```python
result = await client.scrape_url(
    url="https://slow-site.example.com",
    zone="my_zone",
    mode="async",
    poll_timeout=10  # Short timeout
)

if not result.success:
    if "timeout" in result.error.lower():
        print("Scraping timed out - try increasing poll_timeout")
    else:
        print(f"Error: {result.error}")
```

## Performance Characteristics

### Trigger Time

- **Sync mode**: Blocks for entire scrape (~2-10 seconds depending on page)
- **Async mode**: Returns after trigger (~0.5-1 second)

### Total Time

Similar to SERP, total time is comparable - the difference is **blocking** vs **polling**:

```
Sync:  [====== WAIT ======] → HTML
Async: [Trigger] ... [Poll] [Poll] [Poll] → HTML
               ↑
          Do other work here!
```

### Batch Efficiency

Async mode excels for batch scraping:

```python
# Sync mode: Sequential (~30 seconds for 5 URLs)
for url in urls:
    result = await scrape_url(url, mode="sync")  # 6s each

# Async mode: Concurrent (~6-8 seconds for 5 URLs)
results = await scrape_url(urls, mode="async")  # All triggered at once
```

## Error Handling

Async mode returns the same `ScrapeResult` structure:

```python
result = await client.scrape_url(
    url="https://example.com",
    zone="my_zone",
    mode="async",
    poll_timeout=10
)

if result.success:
    print(f"Scraped {len(result.data)} bytes")
    print(f"Root domain: {result.root_domain}")
    print(f"Method: {result.method}")  # "web_unlocker"
else:
    print(f"Error: {result.error}")
    # Common errors:
    # - "Polling timeout after 10s (response_id: ...)"
    # - "Async request failed (response_id: ...)"
    # - "Failed to trigger async request: ..."
```

## Migration from Sync to Async

**Before (Sync):**
```python
result = await client.scrape_url(
    url="https://example.com",
    zone="my_zone"
)
```

**After (Async):**
```python
result = await client.scrape_url(
    url="https://example.com",
    zone="my_zone",
    mode="async",
    poll_interval=2,
    poll_timeout=30
)
```

**No Breaking Changes**: Existing code continues to work (defaults to sync mode).

## Best Practices

1. **Use async for batches**: If scraping >3 URLs, async mode is more efficient
2. **Set reasonable timeouts**: Web scraping can be slower than SERP (30-60s recommended)
3. **Handle errors gracefully**: Always check `result.success` before accessing data
4. **Monitor poll_interval**: 2-5 seconds is optimal (don't poll too aggressively)
5. **Use sync for single pages**: For one-off scrapes, sync is simpler

## Combining SERP and Web Unlocker Async

You can mix both in the same workflow:

```python
async with BrightDataClient() as client:
    # Async search for URLs
    search_result = await client.search.google(
        query="python tutorials",
        zone=client.serp_zone,
        mode="async"
    )

    # Extract URLs from search results
    urls = [r["link"] for r in search_result.data[:5]]

    # Batch scrape those URLs
    scrape_results = await client.scrape_url(
        url=urls,
        zone=client.web_unlocker_zone,
        mode="async",
        poll_timeout=60
    )

    for result in scrape_results:
        if result.success:
            print(f"Scraped: {result.url} ({len(result.data)} bytes)")
```

## See Also

- [Main README](../README.md) - General SDK usage
- [SERP API Endpoints](../devdocs/serp_info.md) - Technical details about endpoints
- [Implementation Plan](../devdocs/enhancements/plan.md) - How async mode was built
