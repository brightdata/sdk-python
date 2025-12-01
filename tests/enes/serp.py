#!/usr/bin/env python3
"""Simple test to demonstrate SERP API raw HTML issue.

How to run manually:
    python probe_tests/test_04_serp_google_simple.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brightdata import BrightDataClient


async def test_serp_raw_html_issue():
    """Test showing SERP returns raw HTML that SDK can't parse."""

    print("SERP API Raw HTML Issue Demonstration")
    print("=" * 60)

    # Initialize client with serp_api1 zone
    client = BrightDataClient(serp_zone="sdk_serp")

    # Initialize engine context
    async with client.engine:
        print("\n🔍 Searching for 'pizza' using Google SERP API...")
        print(f"📍 Zone: {client.serp_zone}")
        print("📋 Payload sent to API: format='json' (hardcoded in SDK)")

        try:
            # Make the search request
            result = await client.search.google_async(query="pizza")

            print("\n✅ API call succeeded")
            print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

            # Show what we got back
            print("\n📊 Result analysis:")
            print(f"   - result.success: {result.success}")
            print(f"   - result.data type: {type(result.data)}")
            print(f"   - result.data length: {len(result.data) if result.data else 0}")

            if result.data and len(result.data) > 0:
                print(f"\n✅ Got {len(result.data)} parsed results")
                first = result.data[0]
                print(f"   First result: {first}")
            else:
                print("\n❌ Got 0 results (empty list)")
                print("\n🔍 Why this happens:")
                print("   1. SDK sends: format='json' (expecting parsed data)")
                print(
                    "   2. API returns: {'status_code': 200, 'headers': {...}, 'body': '<html>...'}"
                )
                print("   3. SDK's normalizer looks for 'organic' field but finds 'body' with HTML")
                print("   4. Normalizer returns empty list since it can't parse HTML")

                # Make a direct API call to show what's really returned
                print("\n📡 Making direct API call to show actual response...")
                from brightdata.api.serp import GoogleSERPService

                service = GoogleSERPService(
                    engine=client.engine,
                    timeout=client.timeout,
                )

                # Temporarily modify the normalizer to show raw data
                original_normalize = service.data_normalizer.normalize
                raw_response = None

                def capture_raw(data):
                    nonlocal raw_response
                    raw_response = data
                    return original_normalize(data)

                service.data_normalizer.normalize = capture_raw

                # Make the request
                await service.search_async(query="pizza", zone=client.serp_zone)

                if raw_response:
                    print("\n📦 Raw API response structure:")
                    if isinstance(raw_response, dict):
                        for key in raw_response.keys():
                            value = raw_response[key]
                            if key == "body" and isinstance(value, str):
                                print(f"   - {key}: HTML string ({len(value)} chars)")
                                print(f"     First 200 chars: {value[:200]}...")
                            elif key == "headers":
                                print(f"   - {key}: {{...}} (response headers)")
                            else:
                                print(f"   - {key}: {value}")

                    print("\n⚠️  The problem:")
                    print(
                        "   - SDK expects: {'organic': [...], 'ads': [...], 'featured_snippet': {...}}"
                    )
                    print(
                        "   - API returns: {'status_code': 200, 'headers': {...}, 'body': '<html>'}"
                    )
                    print("   - Result: SDK can't extract search results from raw HTML")

        except Exception as e:
            print(f"\n❌ Error: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 40)
    print(
        """
The SERP API returns raw HTML but the SDK expects parsed JSON.
This is why all SERP searches return 0 results.

To fix this, either:
1. The SERP zone needs to return parsed data (not raw HTML)
2. The SDK needs an HTML parser (BeautifulSoup, etc.)
3. A different Bright Data service/endpoint should be used
"""
    )


if __name__ == "__main__":
    asyncio.run(test_serp_raw_html_issue())
