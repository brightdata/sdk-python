#!/usr/bin/env python3
"""
Demo script for zone deletion functionality.

This script demonstrates:
1. Listing all zones
2. Creating a test zone
3. Verifying it exists
4. Deleting the test zone
5. Verifying it's gone
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient
from brightdata.exceptions import ZoneError, AuthenticationError


async def demo_delete_zone():
    """Demonstrate zone deletion functionality."""

    print("\n" + "=" * 60)
    print("ZONE DELETION DEMO")
    print("=" * 60)

    # Check for API token
    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        print("Please set BRIGHTDATA_API_TOKEN environment variable")
        return False

    # Create client
    client = BrightDataClient(validate_token=False)

    # Create a unique test zone name
    timestamp = str(int(time.time()))[-6:]
    test_zone_name = f"test_delete_zone_{timestamp}"

    try:
        async with client:
            # Step 1: List initial zones
            print("\n📊 Step 1: Listing current zones...")
            initial_zones = await client.list_zones()
            {z.get("name") for z in initial_zones}
            print(f"✅ Found {len(initial_zones)} zones")

            # Step 2: Create a test zone
            print(f"\n🔧 Step 2: Creating test zone '{test_zone_name}'...")
            test_client = BrightDataClient(
                auto_create_zones=True, web_unlocker_zone=test_zone_name, validate_token=False
            )

            try:
                async with test_client:
                    # Trigger zone creation
                    try:
                        await test_client.scrape_url(
                            url="https://example.com", zone=test_zone_name
                        )
                    except Exception as e:
                        # Zone might be created even if scrape fails
                        print(f"   ℹ️  Scrape error (expected): {e}")

                print(f"✅ Test zone '{test_zone_name}' created")
            except Exception as e:
                print(f"❌ Failed to create test zone: {e}")
                return False

            # Wait a bit for zone to be fully registered
            await asyncio.sleep(2)

            # Step 3: Verify zone exists
            print(f"\n🔍 Step 3: Verifying zone '{test_zone_name}' exists...")
            zones_after_create = await client.list_zones()
            zone_names_after_create = {z.get("name") for z in zones_after_create}

            if test_zone_name in zone_names_after_create:
                print(f"✅ Zone '{test_zone_name}' found in zone list")
                # Print zone details
                test_zone = next(z for z in zones_after_create if z.get("name") == test_zone_name)
                print(f"   Type: {test_zone.get('type', 'unknown')}")
                print(f"   Status: {test_zone.get('status', 'unknown')}")
            else:
                print(f"⚠️  Zone '{test_zone_name}' not found (might still be creating)")

            # Step 4: Delete the test zone
            print(f"\n🗑️  Step 4: Deleting zone '{test_zone_name}'...")
            try:
                await client.delete_zone(test_zone_name)
                print(f"✅ Zone '{test_zone_name}' deleted successfully")
            except ZoneError as e:
                print(f"❌ Failed to delete zone: {e}")
                return False
            except AuthenticationError as e:
                print(f"❌ Authentication error: {e}")
                return False

            # Wait a bit for deletion to propagate
            await asyncio.sleep(2)

            # Step 5: Verify zone is gone
            print(f"\n🔍 Step 5: Verifying zone '{test_zone_name}' is deleted...")
            final_zones = await client.list_zones()
            final_zone_names = {z.get("name") for z in final_zones}

            if test_zone_name not in final_zone_names:
                print(f"✅ Confirmed: Zone '{test_zone_name}' no longer exists")
            else:
                print(
                    f"⚠️  Zone '{test_zone_name}' still appears in list (deletion might be delayed)"
                )

            # Summary
            print("\n" + "=" * 60)
            print("📈 SUMMARY:")
            print(f"   Initial zones: {len(initial_zones)}")
            print(f"   After creation: {len(zones_after_create)}")
            print(f"   After deletion: {len(final_zones)}")
            print(f"   Net change: {len(final_zones) - len(initial_zones)}")

            print("\n" + "=" * 60)
            print("✅ DEMO COMPLETED SUCCESSFULLY")
            print("=" * 60)

            return True

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    try:
        success = asyncio.run(demo_delete_zone())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
