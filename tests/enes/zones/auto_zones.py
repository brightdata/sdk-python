#!/usr/bin/env python3
"""
Test 03: Automatic Zone Creation

This test focuses purely on zone creation - it will attempt to create new zones
regardless of whether similar zones already exist.

How to run manually:
    python probe_tests/test_03_auto_zone_creation.py

Requirements:
    - Valid BRIGHTDATA_API_TOKEN with zone creation permissions
    - Account with ability to create zones

Note: This test will create zones with unique timestamps to ensure new creation.
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brightdata import BrightDataClient


def test_auto_zone_creation():
    """
    Test automatic zone creation feature.

    This test:
    1. Gets initial zone count
    2. Creates client with unique zone names
    3. Triggers zone creation
    4. Shows newly created zones
    """
    print("\n" + "=" * 60)
    print("TEST 3: AUTO ZONE CREATION")
    print("=" * 60)

    print("\n📝 Test Setup:")
    print("   - auto_create_zones=True")
    print("   - Will attempt to create new zones with unique names")
    print("   - Shows newly created zones after creation")

    # Get initial zones
    print("\n🔍 Getting initial zone list...")
    initial_client = BrightDataClient(validate_token=False)
    try:
        initial_info = initial_client.get_account_info_sync()
        initial_zones = initial_info.get("zones", [])
        initial_zone_names = {z.get("name") for z in initial_zones}
        print(f"✅ Initial zones: {len(initial_zones)}")
        if initial_zones:
            for zone in initial_zones:
                print(f"   - {zone.get('name', 'unknown')} (type: {zone.get('type', 'unknown')})")
    except Exception as e:
        print(f"⚠️  Could not get initial zones: {e}")
        initial_zones = []
        initial_zone_names = set()

    # Create unique zone names with timestamp
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp

    print(f"\n🔧 Creating client with unique zone names (suffix: {timestamp})...")

    client = BrightDataClient(
        auto_create_zones=True,
        web_unlocker_zone=f"sdk_unlocker_{timestamp}",
        serp_zone=f"sdk_serp_{timestamp}",
        browser_zone=f"sdk_browser_{timestamp}",
        validate_token=False,
    )

    print("✅ Client initialized with zone names:")
    print(f"   - Web Unlocker: {client.web_unlocker_zone}")
    print(f"   - SERP: {client.serp_zone}")
    print(f"   - Browser: {client.browser_zone}")

    # Trigger zone creation
    print("\n🚀 Triggering zone creation...")
    print("   (Using services to force zone creation)")

    # Run all zone creation attempts in a single async context
    async def attempt_zone_creations():
        results = []

        # Attempt Web Unlocker zone creation
        print(f"\n1️⃣ Attempting to create Web Unlocker zone: {client.web_unlocker_zone}")
        try:
            async with client:
                await client.scrape_url_async(
                    url="https://example.com", zone=client.web_unlocker_zone
                )
                print("   ✅ Zone operation completed")
                results.append(("Web Unlocker", client.web_unlocker_zone, True))
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print("   ⚠️  Zone already exists (name collision)")
            elif "not found" in error_msg:
                print("   ❌ Zone creation failed - zone not found after creation attempt")
                print("   📝 This means auto-creation doesn't actually create zones via API")
            elif "permission" in error_msg or "unauthorized" in error_msg:
                print("   ❌ No permission to create zones")
            else:
                print(f"   ❌ Error: {e}")
            results.append(("Web Unlocker", client.web_unlocker_zone, False))

        # Attempt SERP zone creation
        print(f"\n2️⃣ Attempting to create SERP zone: {client.serp_zone}")
        try:
            async with client:
                await client.search.google_async(query="test", zone=client.serp_zone)
                print("   ✅ Zone operation completed")
                results.append(("SERP", client.serp_zone, True))
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print("   ⚠️  Zone already exists (name collision)")
            elif "not found" in error_msg:
                print("   ❌ Zone creation failed - zone not found after creation attempt")
                print("   📝 This means auto-creation doesn't actually create zones via API")
            elif "permission" in error_msg or "unauthorized" in error_msg:
                print("   ❌ No permission to create zones")
            else:
                print(f"   ❌ Error: {e}")
            results.append(("SERP", client.serp_zone, False))

        return results

    asyncio.run(attempt_zone_creations())

    # Get final zone list
    print("\n📊 Getting final zone list...")
    try:
        final_info = client.get_account_info_sync()
        final_zones = final_info.get("zones", [])
        final_zone_names = {z.get("name") for z in final_zones}

        # Identify newly created zones
        new_zone_names = final_zone_names - initial_zone_names

        print("\n📈 Zone Statistics:")
        print(f"   - Initial zones: {len(initial_zones)}")
        print(f"   - Final zones: {len(final_zones)}")
        print(f"   - Zones added: {len(new_zone_names)}")

        if new_zone_names:
            print(f"\n✅ NEWLY CREATED ZONES ({len(new_zone_names)}):")
            print("   " + "=" * 40)

            for zone in final_zones:
                zone_name = zone.get("name", "unknown")
                if zone_name in new_zone_names:
                    zone_type = zone.get("type", "unknown")
                    zone_status = zone.get("status")
                    zone_created = zone.get("created_at", "unknown")

                    print(f"\n   🆕 {zone_name}")
                    print(f"      Type: {zone_type}")
                    print(f"      Status: {zone_status if zone_status else 'active (null)'}")
                    print(f"      Created: {zone_created}")

                    # Check if this was one of our requested zones
                    if zone_name == client.web_unlocker_zone:
                        print("      ✓ This is our Web Unlocker zone")
                    elif zone_name == client.serp_zone:
                        print("      ✓ This is our SERP zone")
                    elif zone_name == client.browser_zone:
                        print("      ✓ This is our Browser zone")

            print("\n" + "=" * 60)
            print("TEST RESULT: ✅ PASSED")
            print(f"Successfully created {len(new_zone_names)} new zone(s)")
            return True
        else:
            print("\n⚠️  No new zones were created")
            print("\nPossible reasons:")
            print("   1. Auto-creation is disabled for this account")
            print("   2. API token lacks zone creation permissions")
            print("   3. Zone creation requires manual approval")
            print("   4. Account has reached zone limit")

            print("\n" + "=" * 60)
            print("TEST RESULT: ❌ FAILED")
            print("No new zones were created")
            return False

    except Exception as e:
        print(f"\n❌ Error getting final zones: {e}")
        print("\n" + "=" * 60)
        print("TEST RESULT: ❌ ERROR")
        return False


if __name__ == "__main__":
    try:
        # Check for API token
        if not os.environ.get("BRIGHTDATA_API_TOKEN"):
            print("\n❌ ERROR: No API token found")
            print("Please set BRIGHTDATA_API_TOKEN environment variable")
            sys.exit(1)

        success = test_auto_zone_creation()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(3)
