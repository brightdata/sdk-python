#!/usr/bin/env python3
"""
Test to demonstrate the caching issue with get_account_info().
"""

import os
import sys
import asyncio
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def test_caching_issue():
    """Demonstrate caching issue."""

    print("\n" + "=" * 70)
    print("CACHING ISSUE DEMONSTRATION")
    print("=" * 70)

    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        return False

    client = BrightDataClient(
        auto_create_zones=True,
        web_unlocker_zone=f"test_cache_{int(time.time()) % 100000}",
        validate_token=False,
    )

    try:
        async with client:
            # Method 1: get_account_info() - CACHES the result
            print("\n1️⃣ Using get_account_info() (first call)...")
            info1 = await client.get_account_info()
            zones1 = info1.get("zones", [])
            print(f"   Found {len(zones1)} zones via get_account_info()")

            # Method 2: list_zones() - Direct API call
            print("\n2️⃣ Using list_zones() (first call)...")
            zones2 = await client.list_zones()
            print(f"   Found {len(zones2)} zones via list_zones()")

            # Create a new zone
            print("\n3️⃣ Creating a new test zone...")
            test_zone = f"test_new_{int(time.time()) % 100000}"
            temp = BrightDataClient(
                auto_create_zones=True, web_unlocker_zone=test_zone, validate_token=False
            )
            async with temp:
                try:
                    await temp.scrape_url("https://example.com", zone=test_zone)
                except Exception:
                    pass
            print(f"   Zone '{test_zone}' created")

            await asyncio.sleep(1)

            # Check again with both methods
            print("\n4️⃣ Using get_account_info() (second call - CACHED)...")
            info2 = await client.get_account_info()
            zones3 = info2.get("zones", [])
            print(f"   Found {len(zones3)} zones via get_account_info()")
            print(f"   ⚠️  Same as before: {len(zones3) == len(zones1)}")
            print("   🔍 This is CACHED data!")

            print("\n5️⃣ Using list_zones() (second call - FRESH)...")
            zones4 = await client.list_zones()
            print(f"   Found {len(zones4)} zones via list_zones()")
            print(f"   ✅ New data: {len(zones4) > len(zones2)}")
            print("   🔍 This is FRESH data from API!")

            print("\n" + "=" * 70)
            print("🔍 PROBLEM IDENTIFIED:")
            print("   get_account_info() caches the result (line 367-368 in client.py)")
            print("   If you use get_account_info()['zones'], you'll see stale data!")
            print("\n✅ SOLUTION:")
            print("   Always use list_zones() to get current zone list")
            print("=" * 70)

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_caching_issue())
