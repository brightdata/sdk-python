#!/usr/bin/env python3
"""
Cleanup script to delete test zones created during SDK testing.

This script will:
1. List all zones
2. Identify test zones (matching patterns)
3. Ask for confirmation
4. Delete the selected zones
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient
from brightdata.exceptions import ZoneError


async def cleanup_test_zones():
    """Clean up test zones."""

    print("\n" + "=" * 70)
    print("CLEANUP TEST ZONES")
    print("=" * 70)

    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        return False

    client = BrightDataClient(validate_token=False)

    # Patterns to identify test zones
    test_patterns = [
        "sdk_unlocker_",
        "sdk_serp_",
        "test_",
    ]

    # Zones to KEEP (don't delete these)
    keep_zones = [
        "residential",
        "mobile",
        "sdk_unlocker",  # Original zones without timestamps
        "sdk_serp",
    ]

    try:
        async with client:
            print("\n📊 Fetching all zones...")
            all_zones = await client.list_zones()
            print(f"✅ Found {len(all_zones)} total zones")

            # Identify test zones
            test_zones = []
            for zone in all_zones:
                zone_name = zone.get("name", "")

                # Skip zones we want to keep
                if zone_name in keep_zones:
                    continue

                # Check if it matches test patterns
                if any(pattern in zone_name for pattern in test_patterns):
                    test_zones.append(zone)

            if not test_zones:
                print("\n✅ No test zones found to clean up!")
                return True

            print(f"\n🔍 Found {len(test_zones)} test zones to clean up:")
            print("-" * 70)
            for i, zone in enumerate(test_zones, 1):
                zone_name = zone.get("name")
                zone_type = zone.get("type", "unknown")
                print(f"   {i:2d}. {zone_name} ({zone_type})")

            print("-" * 70)
            print(f"\n⚠️  This will delete {len(test_zones)} zones!")
            print("   Zones to KEEP: " + ", ".join(keep_zones))

            # Ask for confirmation
            response = input("\n❓ Delete these zones? (yes/no): ").strip().lower()

            if response not in ["yes", "y"]:
                print("\n❌ Cleanup cancelled by user")
                return False

            # Delete zones
            print(f"\n🗑️  Deleting {len(test_zones)} zones...")
            deleted_count = 0
            failed_count = 0

            for i, zone in enumerate(test_zones, 1):
                zone_name = zone.get("name")
                try:
                    print(f"   [{i}/{len(test_zones)}] Deleting '{zone_name}'...", end=" ")
                    await client.delete_zone(zone_name)
                    print("✅")
                    deleted_count += 1

                    # Small delay to avoid rate limiting
                    if i % 5 == 0:
                        await asyncio.sleep(0.5)

                except ZoneError as e:
                    print(f"❌ ({e})")
                    failed_count += 1
                except Exception as e:
                    print(f"❌ ({e})")
                    failed_count += 1

            # Wait a bit for changes to propagate
            await asyncio.sleep(2)

            # Verify
            print("\n🔍 Verifying cleanup...")
            final_zones = await client.list_zones()
            print(f"✅ Current zone count: {len(final_zones)}")

            # Summary
            print("\n" + "=" * 70)
            print("📊 CLEANUP SUMMARY:")
            print("=" * 70)
            print(f"   Initial zones: {len(all_zones)}")
            print(f"   Test zones found: {len(test_zones)}")
            print(f"   Successfully deleted: {deleted_count}")
            print(f"   Failed to delete: {failed_count}")
            print(f"   Final zone count: {len(final_zones)}")
            print(f"   Zones freed: {len(all_zones) - len(final_zones)}")

            print("\n✅ CLEANUP COMPLETED!")
            print("=" * 70)

            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(cleanup_test_zones())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(2)
