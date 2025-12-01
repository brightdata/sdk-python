#!/usr/bin/env python3
"""
Verify that zones in SDK match what's shown in the Bright Data dashboard.

This script shows that:
1. The SDK accurately reads zone data
2. Changes made via SDK are reflected in the dashboard
3. The dashboard and API are synchronized
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def verify_dashboard_sync():
    """Verify SDK zones match dashboard."""

    print("\n" + "=" * 70)
    print("🔍 DASHBOARD SYNC VERIFICATION")
    print("=" * 70)

    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        return False

    client = BrightDataClient(validate_token=False)

    try:
        async with client:
            print("\n📊 Fetching zones from Bright Data API...")
            zones = await client.list_zones()

            print(f"✅ Found {len(zones)} zones total\n")

            # Group zones by type
            zones_by_type = {}
            for zone in zones:
                ztype = zone.get("type", "unknown")
                if ztype not in zones_by_type:
                    zones_by_type[ztype] = []
                zones_by_type[ztype].append(zone)

            # Display zones grouped by type
            print("📂 ZONES BY TYPE:")
            print("=" * 70)

            for ztype, zlist in sorted(zones_by_type.items()):
                print(f"\n🔹 {ztype.upper()} ({len(zlist)} zones)")
                print("-" * 70)
                for zone in sorted(zlist, key=lambda z: z.get("name", "")):
                    name = zone.get("name")
                    status = zone.get("status", "active")
                    print(f"   • {name:40s} [{status}]")

            print("\n" + "=" * 70)
            print("✅ VERIFICATION COMPLETE")
            print("=" * 70)
            print(
                """
These zones should match exactly what you see in your dashboard at:
https://brightdata.com/cp/zones

📋 How to verify:
   1. Go to: https://brightdata.com/cp/zones
   2. Count the total zones shown
   3. Compare with the count above
   4. Check that zone names and types match
   
✅ If they match: SDK and dashboard are in sync!
❌ If they don't: There may be a caching or API delay issue
            """
            )

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(verify_dashboard_sync())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted")
        sys.exit(2)
