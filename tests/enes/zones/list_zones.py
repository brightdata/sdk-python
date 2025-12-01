#!/usr/bin/env python3
"""
Test 02: List and Analyze Available Zones

This file lists all available zones in your Bright Data account and analyzes
their capabilities for different services (Web Unlocker, SERP, Browser API).

How to run manually:
    python probe_tests/test_02_list_zones.py

Requirements:
    - Valid BRIGHTDATA_API_TOKEN
"""

import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brightdata import BrightDataClient
from brightdata.exceptions import AuthenticationError, APIError


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")


def print_section(title):
    """Print section header."""
    print(f"\n{'-'*40}")
    print(f"{title}")
    print(f"{'-'*40}")


def test_list_zones():
    """List all available zones and their configurations."""
    print_header("BRIGHT DATA ZONES ANALYZER")

    try:
        # Check for API token
        if not os.environ.get("BRIGHTDATA_API_TOKEN"):
            print("\n❌ ERROR: No API token found")
            print("Please set BRIGHTDATA_API_TOKEN environment variable")
            return False

        # Create client
        client = BrightDataClient()
        print("\n✅ Client initialized successfully")

        # Get account info
        print("\nFetching account information...")
        info = client.get_account_info_sync()

        # Display customer info
        print_section("ACCOUNT INFORMATION")
        print(f"Customer ID: {info.get('customer_id', 'Not available')}")
        print(f"Token Valid: {info.get('token_valid', False)}")
        print(f"Retrieved At: {info.get('retrieved_at', 'Unknown')}")

        # Analyze zones
        zones = info.get("zones", [])
        print(f"\nTotal Zones: {len(zones)}")

        if not zones:
            print("\n⚠️  No zones found in your account")
            print("\nTo create zones:")
            print("1. Log in to https://brightdata.com")
            print("2. Navigate to Zones section")
            print("3. Create zones for Web Unlocker, SERP, or Browser API")
            return False

        # List all zones with details
        print_section("AVAILABLE ZONES")

        for i, zone in enumerate(zones, 1):
            print(f"\nZone {i}:")
            print(f"  Name: {zone.get('name', 'Unknown')}")
            print(f"  Status: {zone.get('status', 'Unknown')}")

            # Check plan details if available
            plan = zone.get("plan", {})
            if plan:
                print(f"  Plan Type: {plan.get('type', 'Unknown')}")
                print(f"  Plan Description: {plan.get('description', 'N/A')}")

            # Creation date if available
            created = zone.get("created")
            if created:
                print(f"  Created: {created}")

            # Try to determine zone capabilities based on name/plan
            zone_name = zone.get("name", "").lower()
            capabilities = []

            if "unlocker" in zone_name or "unblocker" in zone_name:
                capabilities.append("Web Unlocker")
            if "serp" in zone_name or "search" in zone_name:
                capabilities.append("SERP/Search")
            if "browser" in zone_name or "scraper" in zone_name:
                capabilities.append("Browser/Scraper")
            if "residential" in zone_name:
                capabilities.append("Residential Proxy")
            if "datacenter" in zone_name:
                capabilities.append("Datacenter Proxy")

            if capabilities:
                print(f"  Likely Capabilities: {', '.join(capabilities)}")

        # Suggest zone configuration
        print_section("ZONE CONFIGURATION SUGGESTIONS")

        # Check for Web Unlocker zone
        unlocker_zones = [z for z in zones if "unlocker" in z.get("name", "").lower()]
        if unlocker_zones:
            print(f"✅ Web Unlocker zone found: {unlocker_zones[0].get('name')}")
            print(f"   Use: BrightDataClient(web_unlocker_zone='{unlocker_zones[0].get('name')}')")
        else:
            print("❌ No Web Unlocker zone found")
            print("   Suggestion: Create a zone with Web Unlocker service enabled")

        # Check for SERP zone
        serp_zones = [z for z in zones if "serp" in z.get("name", "").lower()]
        if serp_zones:
            print(f"\n✅ SERP zone found: {serp_zones[0].get('name')}")
            print(f"   Use: BrightDataClient(serp_zone='{serp_zones[0].get('name')}')")
        else:
            print("\n❌ No SERP zone found")
            print("   Suggestion: Create a zone with SERP API service enabled")

        # Check for Browser zone
        browser_zones = [
            z
            for z in zones
            if "browser" in z.get("name", "").lower() or "scraper" in z.get("name", "").lower()
        ]
        if browser_zones:
            print(f"\n✅ Browser/Scraper zone found: {browser_zones[0].get('name')}")
            print(f"   Use: BrightDataClient(browser_zone='{browser_zones[0].get('name')}')")
        else:
            print("\n❌ No Browser/Scraper zone found")
            print("   Suggestion: Create a zone with Browser API or Web Scraper service")

        # Test zone connectivity
        print_section("ZONE CONNECTIVITY TEST")

        if zones:
            # Try to use the first zone for a test
            first_zone = zones[0].get("name")
            print(f"\nTesting with zone: {first_zone}")

            try:
                # Create client with specific zone
                test_client = BrightDataClient(web_unlocker_zone=first_zone)

                # Try a simple scrape
                print(f"Attempting to scrape with zone '{first_zone}'...")
                result = test_client.scrape_url("https://httpbin.org/html", zone=first_zone)

                if result.success:
                    print(f"✅ Zone '{first_zone}' is working!")
                    print(f"   Data received: {len(str(result.data)) if result.data else 0} chars")
                else:
                    print(f"❌ Zone '{first_zone}' returned error: {result.error}")

            except Exception as e:
                print(f"❌ Zone test failed: {e}")

        # Export zones to file
        print_section("EXPORT ZONES")

        export_file = Path("probe_tests/zones_config.json")
        zones_data = {
            "customer_id": info.get("customer_id"),
            "timestamp": datetime.now().isoformat(),
            "zones": zones,
            "recommendations": {
                "web_unlocker_zone": unlocker_zones[0].get("name") if unlocker_zones else None,
                "serp_zone": serp_zones[0].get("name") if serp_zones else None,
                "browser_zone": browser_zones[0].get("name") if browser_zones else None,
            },
        }

        try:
            export_file.write_text(json.dumps(zones_data, indent=2))
            print(f"✅ Zones configuration exported to: {export_file}")
            print("   You can use this file to configure your SDK")
        except Exception as e:
            print(f"❌ Failed to export zones: {e}")

        # Summary
        print_section("SUMMARY")
        print(f"Total zones found: {len(zones)}")
        print(f"Web Unlocker zones: {len(unlocker_zones)}")
        print(f"SERP zones: {len(serp_zones)}")
        print(f"Browser zones: {len(browser_zones)}")

        # Configuration recommendation
        if zones:
            print("\n📝 RECOMMENDED CLIENT CONFIGURATION:")
            print("```python")
            print("from brightdata import BrightDataClient")
            print()
            print("client = BrightDataClient(")
            if unlocker_zones:
                print(f'    web_unlocker_zone="{unlocker_zones[0].get("name")}",')
            if serp_zones:
                print(f'    serp_zone="{serp_zones[0].get("name")}",')
            if browser_zones:
                print(f'    browser_zone="{browser_zones[0].get("name")}",')
            print(")")
            print("```")

        return True

    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("Please check your API token")
        return False

    except APIError as e:
        print(f"\n❌ API error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run zone listing and analysis."""
    try:
        success = test_list_zones()

        if success:
            print("\n✅ Zone analysis completed successfully!")
            return 0
        else:
            print("\n❌ Zone analysis failed or incomplete")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 2

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
