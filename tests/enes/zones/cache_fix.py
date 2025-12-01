#!/usr/bin/env python3
"""
Demonstrate the caching issue and the fix.
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def demo_caching():
    """Demonstrate caching behavior."""

    print("\n" + "=" * 70)
    print("ZONE LISTING - CACHING BEHAVIOR")
    print("=" * 70)

    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        return False

    client = BrightDataClient(validate_token=False)

    try:
        async with client:
            # Method 1: get_account_info() - caches by default
            print("\n📊 Method 1: get_account_info() [CACHED by default]")
            print("-" * 70)

            print("   First call...")
            info1 = await client.get_account_info()
            zones1 = info1.get("zones", [])
            print(f"   ✓ Found {len(zones1)} zones")

            print("\n   Second call (returns CACHED data)...")
            info2 = await client.get_account_info()
            zones2 = info2.get("zones", [])
            print(f"   ✓ Found {len(zones2)} zones")
            print(f"   ℹ️  Same object: {info1 is info2}")

            print("\n   Third call with refresh=True (fetches FRESH data)...")
            info3 = await client.get_account_info(refresh=True)
            zones3 = info3.get("zones", [])
            print(f"   ✓ Found {len(zones3)} zones")
            print(f"   ℹ️  Different object: {info1 is not info3}")

            # Method 2: list_zones() - always fresh
            print("\n\n📋 Method 2: list_zones() [ALWAYS FRESH]")
            print("-" * 70)

            print("   First call...")
            zones4 = await client.list_zones()
            print(f"   ✓ Found {len(zones4)} zones")

            print("\n   Second call (fetches FRESH data)...")
            zones5 = await client.list_zones()
            print(f"   ✓ Found {len(zones5)} zones")
            print(f"   ℹ️  Different objects: {zones4 is not zones5}")

            # Summary
            print("\n\n" + "=" * 70)
            print("📝 RECOMMENDATIONS:")
            print("=" * 70)
            print(
                """
   ✅ For listing zones after creation/deletion:
      Use: await client.list_zones()
      
   ✅ For general account info (cached):
      Use: await client.get_account_info()
      
   ✅ For fresh account info (after zone changes):
      Use: await client.get_account_info(refresh=True)
      
   ⚠️  AVOID: Using get_account_info()['zones'] without refresh
      This returns cached data that may be stale!
            """
            )
            print("=" * 70)

            # Show some zones
            print("\n📂 Current Zones (sample):")
            for i, zone in enumerate(zones4[:10]):
                print(f"   {i+1}. {zone.get('name')} ({zone.get('type')})")
            if len(zones4) > 10:
                print(f"   ... and {len(zones4) - 10} more")

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(demo_caching())
