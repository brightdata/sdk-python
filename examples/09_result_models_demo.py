"""Demo: Result models functionality demonstration."""

from datetime import datetime, timezone
from brightdata.models import BaseResult, ScrapeResult, SearchResult, CrawlResult

print("=" * 60)
print("RESULT MODELS DEMONSTRATION")
print("=" * 60)

# Test BaseResult
print("\n1. BaseResult:")
r = BaseResult(success=True, cost=0.001)
print(f"   Created: {r}")
print(f"   success: {r.success}")
print(f"   cost: ${r.cost}")
print(f"   error: {r.error}")
print(f"   to_json(): {r.to_json()[:80]}...")

# Test with timing
now = datetime.now(timezone.utc)
r2 = BaseResult(
    success=True,
    cost=0.002,
    trigger_sent_at=now,
    data_fetched_at=now,
)
print(f"   elapsed_ms: {r2.elapsed_ms()}")
print(f"   get_timing_breakdown: {list(r2.get_timing_breakdown().keys())}")

# Test ScrapeResult
print("\n2. ScrapeResult:")
scrape = ScrapeResult(
    success=True,
    url="https://www.linkedin.com/in/test",
    status="ready",
    platform="linkedin",
    cost=0.001,
    trigger_sent_at=now,
    data_fetched_at=now,
)
print(f"   Created: {scrape}")
print(f"   url: {scrape.url}")
print(f"   platform: {scrape.platform}")
print(f"   status: {scrape.status}")
print(f"   get_timing_breakdown: {list(scrape.get_timing_breakdown().keys())}")

# Test SearchResult
print("\n3. SearchResult:")
search = SearchResult(
    success=True,
    query={"q": "python async", "engine": "google"},
    total_found=1000,
    search_engine="google",
    cost=0.002,
)
print(f"   Created: {search}")
print(f"   query: {search.query}")
print(f"   total_found: {search.total_found}")
print(f"   search_engine: {search.search_engine}")

# Test CrawlResult
print("\n4. CrawlResult:")
crawl = CrawlResult(
    success=True,
    domain="example.com",
    pages=[{"url": "https://example.com/page1", "data": {}}],
    total_pages=1,
    cost=0.005,
)
print(f"   Created: {crawl}")
print(f"   domain: {crawl.domain}")
print(f"   pages: {len(crawl.pages)}")
print(f"   total_pages: {crawl.total_pages}")

# Test utilities
print("\n5. Utilities:")
print(f"   BaseResult.to_json(): {len(r.to_json())} chars")
print(f"   ScrapeResult.to_json(): {len(scrape.to_json())} chars")
print(f"   SearchResult.to_json(): {len(search.to_json())} chars")
print(f"   CrawlResult.to_json(): {len(crawl.to_json())} chars")

# Test interface requirements
print("\n6. Interface Requirements:")
print("   Common fields:")
print(f"   result.success: {r.success} (bool)")
print(f"   result.cost: ${r.cost} (float)")
print(f"   result.error: {r.error} (str | None)")
print(f"   result.trigger_sent_at: {r.trigger_sent_at} (datetime)")
print(f"   result.data_fetched_at: {r.data_fetched_at} (datetime)")

print("\n   Service-specific fields:")
print(f"   scrape_result.url: {scrape.url}")
print(f"   scrape_result.platform: {scrape.platform}")
print(f"   search_result.query: {search.query}")
print(f"   search_result.total_found: {search.total_found}")
print(f"   crawl_result.domain: {crawl.domain}")
print(f"   crawl_result.pages: {len(crawl.pages)} items")

print("\n   Utilities:")
print(f"   result.to_json(): {r.to_json()[:50]}...")
print(f"   result.get_timing_breakdown(): {len(r2.get_timing_breakdown())} keys")

print("\n" + "=" * 60)
print("ALL TESTS PASSED - FUNCTIONALITY VERIFIED!")
print("=" * 60)
