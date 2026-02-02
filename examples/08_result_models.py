"""Example: Using unified result models."""

from datetime import datetime
from brightdata.models import ScrapeResult, SearchResult, CrawlResult


def example_scrape_result():
    """Example of using ScrapeResult."""
    print("=== ScrapeResult Example ===\n")

    # Create a scrape result
    result = ScrapeResult(
        success=True,
        url="https://www.amazon.com/dp/B0CRMZHDG8",
        platform="amazon",
        cost=0.001,
        snapshot_id="snapshot_12345",
        data={"product": "Example Product", "price": "$29.99"},
        trigger_sent_at=datetime.utcnow(),
        data_fetched_at=datetime.utcnow(),
        root_domain="amazon.com",
        row_count=1,
    )

    print(f"Result: {result}")
    print(f"Success: {result.success}")
    print(f"URL: {result.url}")
    print(f"Platform: {result.platform}")
    print(f"Cost: ${result.cost:.4f}")
    print(f"Elapsed: {result.elapsed_ms():.2f} ms")
    print("\nTiming Breakdown:")
    for key, value in result.get_timing_breakdown().items():
        print(f"  {key}: {value}")

    # Serialize to JSON
    print("\nJSON representation:")
    print(result.to_json(indent=2))

    # Save to file
    result.save_to_file("scrape_result.json", format="json")
    print("\nSaved to scrape_result.json")


def example_search_result():
    """Example of using SearchResult."""
    print("\n\n=== SearchResult Example ===\n")

    result = SearchResult(
        success=True,
        query={"q": "python async", "engine": "google", "country": "us"},
        search_engine="google",
        country="us",
        total_found=1000000,
        page=1,
        results_per_page=10,
        data=[
            {"title": "Python AsyncIO", "url": "https://example.com/1"},
            {"title": "Async Python Guide", "url": "https://example.com/2"},
        ],
        cost=0.002,
        trigger_sent_at=datetime.utcnow(),
        data_fetched_at=datetime.utcnow(),
    )

    print(f"Result: {result}")
    print(f"Query: {result.query}")
    print(f"Total Found: {result.total_found:,}")
    print(f"Results: {len(result.data) if result.data else 0} items")
    print(f"Cost: ${result.cost:.4f}")

    # Get timing breakdown
    print("\nTiming Breakdown:")
    for key, value in result.get_timing_breakdown().items():
        print(f"  {key}: {value}")


def example_crawl_result():
    """Example of using CrawlResult."""
    print("\n\n=== CrawlResult Example ===\n")

    result = CrawlResult(
        success=True,
        domain="example.com",
        start_url="https://example.com",
        total_pages=5,
        depth=2,
        pages=[
            {"url": "https://example.com/page1", "status": 200, "data": {}},
            {"url": "https://example.com/page2", "status": 200, "data": {}},
        ],
        cost=0.005,
        crawl_started_at=datetime.utcnow(),
        crawl_completed_at=datetime.utcnow(),
    )

    print(f"Result: {result}")
    print(f"Domain: {result.domain}")
    print(f"Total Pages: {result.total_pages}")
    print(f"Depth: {result.depth}")
    print(f"Pages Crawled: {len(result.pages)}")
    print(f"Cost: ${result.cost:.4f}")

    # Get timing breakdown
    print("\nTiming Breakdown:")
    for key, value in result.get_timing_breakdown().items():
        print(f"  {key}: {value}")


def example_error_handling():
    """Example of error handling with result models."""
    print("\n\n=== Error Handling Example ===\n")

    # Failed scrape
    error_result = ScrapeResult(
        success=False,
        url="https://example.com/failed",
        status="error",
        error="Connection timeout after 30 seconds",
        cost=0.0,  # No charge for failed requests
        trigger_sent_at=datetime.utcnow(),
        data_fetched_at=datetime.utcnow(),
    )

    print(f"Error Result: {error_result}")
    print(f"Success: {error_result.success}")
    print(f"Error: {error_result.error}")
    print(f"Cost: ${error_result.cost:.4f}")

    # Check if operation succeeded
    if not error_result.success:
        print(f"\nOperation failed: {error_result.error}")
        print("Timing information still available:")
        print(error_result.get_timing_breakdown())


def example_serialization():
    """Example of serialization methods."""
    print("\n\n=== Serialization Example ===\n")

    result = ScrapeResult(
        success=True,
        url="https://example.com",
        cost=0.001,
        data={"key": "value"},
    )

    # Convert to dictionary
    result_dict = result.to_dict()
    print("Dictionary representation:")
    print(result_dict)

    # Convert to JSON
    json_str = result.to_json(indent=2)
    print("\nJSON representation:")
    print(json_str)

    # Save to different formats
    result.save_to_file("result.json", format="json")
    result.save_to_file("result.txt", format="txt")
    print("\nSaved to result.json and result.txt")


if __name__ == "__main__":
    example_scrape_result()
    example_search_result()
    example_crawl_result()
    example_error_handling()
    example_serialization()
