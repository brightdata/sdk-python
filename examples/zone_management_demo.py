"""
Zone Management Demo - Demonstrates zone creation and management features.

This example shows how to:
1. List existing zones
2. Enable automatic zone creation
3. Use ZoneManager for advanced zone management
"""

import asyncio
import os
from brightdata import BrightDataClient, ZoneManager


async def demo_list_zones():
    """List all zones in the account."""
    print("\n" + "=" * 60)
    print("DEMO 1: List Zones")
    print("=" * 60)

    client = BrightDataClient()

    # List all zones
    zones = await client.list_zones()

    print(f"\nFound {len(zones)} zones in your account:")
    for zone in zones:
        zone_name = zone.get("name", "Unknown")
        zone_type = zone.get("type", "unknown")
        zone_status = zone.get("status", "unknown")
        print(f"  - {zone_name}")
        print(f"    Type: {zone_type}")
        print(f"    Status: {zone_status}")
        print()


async def demo_auto_create_zones():
    """Demonstrate automatic zone creation."""
    print("\n" + "=" * 60)
    print("DEMO 2: Automatic Zone Creation")
    print("=" * 60)

    # Create client with auto zone creation enabled
    client = BrightDataClient(auto_create_zones=True)

    print("\nClient configured with auto_create_zones=True")
    print("Required zones will be created automatically on first API call:")
    print("  - sdk_unlocker (Web Unlocker)")
    print("  - sdk_serp (SERP API)")
    print("  - sdk_browser (Browser API)")

    # Zones will be created when entering context manager
    async with client:
        print("\n✓ Zones ensured (created if missing)")

        # List zones to confirm
        zones = await client.list_zones()
        zone_names = [z.get("name") for z in zones]

        print(f"\nZones now in account ({len(zones)} total):")
        for name in zone_names:
            print(f"  - {name}")


async def demo_zone_manager_advanced():
    """Demonstrate advanced zone management with ZoneManager."""
    print("\n" + "=" * 60)
    print("DEMO 3: Advanced Zone Management")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        zone_manager = ZoneManager(client.engine)

        print("\nUsing ZoneManager for fine-grained control...")

        # List zones
        zones = await zone_manager.list_zones()
        print(f"\nCurrent zones: {len(zones)}")

        # Ensure specific zones exist
        print("\nEnsuring custom zones exist...")
        print("  - my_web_unlocker (unblocker)")
        print("  - my_serp_api (serp)")

        try:
            await zone_manager.ensure_required_zones(
                web_unlocker_zone="my_web_unlocker", serp_zone="my_serp_api"
            )
            print("\n✓ Zones ensured successfully")
        except Exception as e:
            print(f"\n✗ Zone creation failed: {e}")

        # List zones again
        zones = await zone_manager.list_zones()
        print(f"\nZones after creation: {len(zones)}")
        for zone in zones:
            print(f"  - {zone.get('name')}")


async def demo_sync_methods():
    """Demonstrate synchronous zone listing."""
    print("\n" + "=" * 60)
    print("DEMO 4: Synchronous Zone Listing")
    print("=" * 60)

    client = BrightDataClient()

    print("\nUsing synchronous method for convenience...")

    # Synchronous version (blocks until complete)
    zones = client.list_zones_sync()

    print(f"\nFound {len(zones)} zones (synchronous call):")
    for zone in zones[:5]:  # Show first 5
        print(f"  - {zone.get('name')}: {zone.get('type', 'unknown')}")

    if len(zones) > 5:
        print(f"  ... and {len(zones) - 5} more")


async def main():
    """Run all zone management demos."""
    print("\n" + "=" * 60)
    print("BRIGHT DATA SDK - ZONE MANAGEMENT DEMOS")
    print("=" * 60)

    # Check for API token
    if not os.getenv("BRIGHTDATA_API_TOKEN"):
        print("\n⚠️  Warning: BRIGHTDATA_API_TOKEN not set")
        print("Please set your API token as an environment variable:")
        print("  export BRIGHTDATA_API_TOKEN='your_token_here'")
        return

    try:
        # Demo 1: List zones
        await demo_list_zones()

        # Demo 2: Auto-create zones
        # Note: Uncomment to test zone creation
        # await demo_auto_create_zones()

        # Demo 3: Advanced zone management
        # Note: Uncomment to test custom zone creation
        # await demo_zone_manager_advanced()

        # Demo 4: Sync methods
        await demo_sync_methods()

        print("\n" + "=" * 60)
        print("DEMOS COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
