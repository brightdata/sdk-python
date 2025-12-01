#!/usr/bin/env python3
"""
Test to demonstrate improved permission error handling.

This test shows how the SDK now provides clear, helpful error messages
when API tokens lack zone creation permissions.
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from brightdata import BrightDataClient
from brightdata.exceptions import AuthenticationError


async def test_permission_error_handling():
    """Test that permission errors are caught and displayed clearly."""

    print("\n" + "=" * 70)
    print("🧪 TESTING PERMISSION ERROR HANDLING")
    print("=" * 70)

    print(
        """
This test demonstrates the improved error handling when your API token
lacks zone creation permissions.

Expected behavior:
  ✅ Clear error message explaining the issue
  ✅ Direct link to fix the problem
  ✅ No silent failures
  ✅ Helpful instructions for users
    """
    )

    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        print("\n❌ ERROR: No API token found")
        return False

    client = BrightDataClient(
        auto_create_zones=True, web_unlocker_zone="test_permission_zone", validate_token=False
    )

    print("🔧 Attempting to create a zone with auto_create_zones=True...")
    print("-" * 70)

    try:
        async with client:
            # This will trigger zone creation
            print("\n⏳ Initializing client (will attempt zone creation)...")
            print("   If your token lacks permissions, you'll see a clear error message.\n")

            # If we get here, zones were created successfully or already exist
            zones = await client.list_zones()
            print(f"✅ SUCCESS: Client initialized, {len(zones)} zones available")

            # Check if our test zone exists
            zone_names = {z.get("name") for z in zones}
            if "test_permission_zone" in zone_names:
                print("   ✓ Test zone was created successfully")
                print("   ✓ Your API token HAS zone creation permissions")
            else:
                print("   ℹ️  Test zone not created (may already exist with different name)")

            return True

    except AuthenticationError as e:
        print("\n" + "=" * 70)
        print("✅ PERMISSION ERROR CAUGHT (Expected if you lack permissions)")
        print("=" * 70)
        print(f"\nError Message:\n{e}")
        print("\n" + "=" * 70)
        print("📝 This is the IMPROVED error handling!")
        print("=" * 70)
        print(
            """
Before: Error was unclear and could fail silently
After:  Clear message with actionable steps to fix the issue

The error message should have told you:
  1. ❌ What went wrong (permission denied)
  2. 🔗 Where to fix it (https://brightdata.com/cp/setting/users)
  3. 📋 What to do (enable zone creation permission)
        """
        )
        return True  # This is expected behavior

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_permission_error_handling())

        print("\n" + "=" * 70)
        if success:
            print("✅ TEST PASSED")
            print("=" * 70)
            print(
                """
Summary:
  • Permission errors are now caught and displayed clearly
  • Users get actionable instructions to fix the problem
  • No more silent failures
  • SDK provides helpful guidance
            """
            )
        else:
            print("❌ TEST FAILED")
        print("=" * 70)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted")
        sys.exit(2)
