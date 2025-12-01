#!/usr/bin/env python3
"""Test Amazon scraper to verify API fetches data correctly.

How to run manually:
    python tests/enes/amazon.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def test_amazon_products():
    """Test Amazon product scraping."""

    print("=" * 60)
    print("AMAZON SCRAPER TEST - Products")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.amazon
        async with scraper.engine:
            print("\n🛒 Testing Amazon product scraping...")
            print("📍 Product URL: https://www.amazon.com/dp/B0CRMZHDG8")

            try:
                result = await scraper.products_async(
                    url="https://www.amazon.com/dp/B0CRMZHDG8", timeout=240
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")
                print(
                    f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}"
                )
                print(f"   - result.error: {result.error if hasattr(result, 'error') else 'N/A'}")

                if result.data:
                    print("\n✅ Got product data:")
                    if isinstance(result.data, dict):
                        print(f"   - Title: {result.data.get('title', 'N/A')}")
                        print(f"   - Price: {result.data.get('price', 'N/A')}")
                        print(f"   - ASIN: {result.data.get('asin', 'N/A')}")
                        print(f"   - Rating: {result.data.get('rating', 'N/A')}")
                        print(f"   - Review Count: {result.data.get('reviews_count', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No product data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_amazon_reviews():
    """Test Amazon reviews scraping."""

    print("\n\n" + "=" * 60)
    print("AMAZON SCRAPER TEST - Reviews")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.amazon
        async with scraper.engine:
            print("\n📝 Testing Amazon reviews scraping...")
            print("📍 Product URL: https://www.amazon.com/dp/B0CRMZHDG8")
            print("📋 Parameters: pastDays=30, numOfReviews=10")

            try:
                result = await scraper.reviews_async(
                    url="https://www.amazon.com/dp/B0CRMZHDG8",
                    pastDays=30,
                    numOfReviews=10,
                    timeout=240,
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")
                print(
                    f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}"
                )
                print(f"   - result.error: {result.error if hasattr(result, 'error') else 'N/A'}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} reviews:")
                        for i, review in enumerate(result.data[:3], 1):
                            print(f"\n   Review {i}:")
                            print(f"   - Rating: {review.get('rating', 'N/A')}")
                            print(f"   - Title: {review.get('title', 'N/A')[:60]}...")
                            print(f"   - Author: {review.get('author', 'N/A')}")
                    elif isinstance(result.data, dict):
                        reviews = result.data.get("reviews", [])
                        print(f"\n✅ Got {len(reviews)} reviews")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No reviews data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Amazon Scraper Tests\n")
    asyncio.run(test_amazon_products())
    asyncio.run(test_amazon_reviews())
    print("\n" + "=" * 60)
    print("✅ Amazon tests completed")
    print("=" * 60)
