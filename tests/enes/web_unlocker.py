#!/usr/bin/env python3
"""Test Web Unlocker (Generic Scraper) to verify API fetches data correctly.

How to run manually:
    python tests/enes/web_unlocker.py
"""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient

# Create samples directory
SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "web_unlocker"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)


async def test_web_unlocker_single_url():
    """Test Web Unlocker with a single URL."""

    print("=" * 60)
    print("WEB UNLOCKER TEST - Single URL")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        print("\n🌐 Testing Web Unlocker with single URL...")
        print("📍 URL: https://httpbin.org/html")

        try:
            result = await client.scrape_url(
                url="https://httpbin.org/html", response_format="raw"
            )

            print("\n✅ API call succeeded")
            print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

            print("\n📊 Result analysis:")
            print(f"   - result.success: {result.success}")
            print(f"   - result.data type: {type(result.data)}")
            print(f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}")
            print(f"   - result.error: {result.error if hasattr(result, 'error') else 'N/A'}")
            print(f"   - result.method: {result.method if hasattr(result, 'method') else 'N/A'}")

            if result.data:
                print("\n✅ Got data:")
                if isinstance(result.data, str):
                    print(f"   - Data length: {len(result.data)} characters")
                    print(f"   - First 200 chars: {result.data[:200]}...")
                    print(f"   - Contains HTML: {'<html' in result.data.lower()}")

                    # Save to file
                    output_file = SAMPLES_DIR / "single_url_raw.html"
                    output_file.write_text(result.data)
                    print(f"\n💾 Saved response to: {output_file}")
                else:
                    print(f"   Data: {result.data}")
            else:
                print("\n❌ No data returned")

            return result

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


async def test_web_unlocker_json_format():
    """Test Web Unlocker with JSON response format."""

    print("\n\n" + "=" * 60)
    print("WEB UNLOCKER TEST - JSON Format")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        print("\n🌐 Testing Web Unlocker with JSON response format...")
        print("📍 URL: https://httpbin.org/json")

        try:
            result = await client.scrape_url(
                url="https://httpbin.org/json", response_format="json"
            )

            print("\n✅ API call succeeded")
            print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

            print("\n📊 Result analysis:")
            print(f"   - result.success: {result.success}")
            print(f"   - result.data type: {type(result.data)}")
            print(f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}")
            print(f"   - result.method: {result.method if hasattr(result, 'method') else 'N/A'}")

            if result.data:
                print("\n✅ Got JSON data:")
                if isinstance(result.data, dict):
                    print(f"   - Keys: {list(result.data.keys())}")
                    for key, value in list(result.data.items())[:5]:
                        print(f"   - {key}: {str(value)[:100]}")

                    # Save to file
                    output_file = SAMPLES_DIR / "single_url_json.json"
                    output_file.write_text(json.dumps(result.data, indent=2))
                    print(f"\n💾 Saved response to: {output_file}")
                else:
                    print(f"   Data: {result.data}")
            else:
                print("\n❌ No data returned")

            return result

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


async def test_web_unlocker_multiple_urls():
    """Test Web Unlocker with multiple URLs concurrently."""

    print("\n\n" + "=" * 60)
    print("WEB UNLOCKER TEST - Multiple URLs")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        print("\n🌐 Testing Web Unlocker with multiple URLs...")
        urls = ["https://httpbin.org/html", "https://httpbin.org/delay/1", "https://example.com"]
        print(f"📋 URLs: {len(urls)} URLs")

        try:
            results = await client.scrape_url(url=urls, response_format="raw")

            print("\n✅ API call succeeded")
            print(f"📊 Got {len(results)} results")

            for i, result in enumerate(results, 1):
                print(f"\n   Result {i}:")
                print(f"   - URL: {result.url if hasattr(result, 'url') else 'N/A'}")
                print(f"   - Success: {result.success}")
                print(f"   - Status: {result.status if hasattr(result, 'status') else 'N/A'}")

                if result.success and result.data:
                    if isinstance(result.data, str):
                        print(f"   - Data length: {len(result.data)} characters")
                        print(f"   - Contains HTML: {'<html' in result.data.lower()}")

                        # Save to file
                        output_file = SAMPLES_DIR / f"multiple_urls_{i}.html"
                        output_file.write_text(result.data)
                        print(f"   - Saved to: {output_file}")
                    else:
                        print(f"   - Data type: {type(result.data)}")
                else:
                    print(f"   - Error: {result.error if hasattr(result, 'error') else 'N/A'}")

                if hasattr(result, "elapsed_ms") and result.elapsed_ms():
                    print(f"   - Elapsed: {result.elapsed_ms():.2f}ms")

            return results

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


async def test_web_unlocker_with_country():
    """Test Web Unlocker with country targeting."""

    print("\n\n" + "=" * 60)
    print("WEB UNLOCKER TEST - Country Targeting")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        print("\n🌐 Testing Web Unlocker with country targeting...")
        print("📍 URL: https://httpbin.org/headers")
        print("🌍 Country: US")

        try:
            result = await client.scrape_url(
                url="https://httpbin.org/headers", country="us", response_format="raw"
            )

            print("\n✅ API call succeeded")
            print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

            print("\n📊 Result analysis:")
            print(f"   - result.success: {result.success}")
            print(f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}")

            if result.data:
                print("\n✅ Got data:")
                if isinstance(result.data, str):
                    print(f"   - Data length: {len(result.data)} characters")
                    print(f"   - First 300 chars: {result.data[:300]}...")

                    # Save to file
                    output_file = SAMPLES_DIR / "country_targeting.html"
                    output_file.write_text(result.data)
                    print(f"\n💾 Saved response to: {output_file}")
                else:
                    print(f"   Data: {result.data}")
            else:
                print("\n❌ No data returned")

            return result

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Web Unlocker Tests\n")
    asyncio.run(test_web_unlocker_single_url())
    asyncio.run(test_web_unlocker_json_format())
    asyncio.run(test_web_unlocker_multiple_urls())
    asyncio.run(test_web_unlocker_with_country())
    print("\n" + "=" * 60)
    print("✅ Web Unlocker tests completed")
    print("=" * 60)
