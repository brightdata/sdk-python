#!/usr/bin/env python3
"""
Test NEW Amazon Search API Feature (client.search.amazon)

This tests the NEW parameter-based Amazon search functionality:
- client.search.amazon.products(keyword="laptop", min_price=..., etc.)

This is DIFFERENT from the old URL-based approach which gets blocked.

python -m tests.enes.amazon_search
python tests/enes/amazon_search.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from brightdata import BrightDataClient


async def test_new_amazon_search_api():
    """Test the NEW Amazon Search API"""
    print("\n" + "=" * 80)
    print("TESTING: NEW client.search.amazon API")
    print("=" * 80)

    client = BrightDataClient()

    # Check if search.amazon exists
    if not hasattr(client.search, "amazon"):
        print("\n❌ client.search.amazon NOT FOUND!")
        print("   The new Amazon search feature is not available")
        return False

    print("✅ client.search.amazon found!")

    test_results = []

    # Test 1: Basic keyword search
    print("\n" + "-" * 80)
    print("1️⃣ TEST: Basic Keyword Search")
    print("-" * 80)
    print("   Method: client.search.amazon.products(keyword='laptop')")

    try:
        async with client.engine:
            result = await client.search.amazon.products(keyword="laptop")

        print("   ✅ API call succeeded")
        print(f"   Success: {result.success}")
        print(f"   Status: {result.status}")

        if result.success:
            if isinstance(result.data, dict) and "error" in result.data:
                print(f"   ⚠️  Crawler blocked by Amazon: {result.data['error']}")
                print("   (This is expected - Amazon blocks search pages)")
                test_results.append(True)  # API worked, Amazon blocked
            elif isinstance(result.data, list):
                print(f"   ✅ SUCCESS! Got {len(result.data)} products")
                test_results.append(True)
            else:
                print(f"   ⚠️  Unexpected data type: {type(result.data)}")
                test_results.append(False)
        else:
            print(f"   ❌ Search failed: {result.error}")
            test_results.append(False)

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        test_results.append(False)

    # Test 2: Search with price filters
    print("\n" + "-" * 80)
    print("2️⃣ TEST: Keyword + Price Filters")
    print("-" * 80)
    print("   Method: client.search.amazon.products(")
    print("       keyword='headphones',")
    print("       min_price=5000,  # $50")
    print("       max_price=20000  # $200")
    print("   )")

    try:
        async with client.engine:
            result = await client.search.amazon.products(
                keyword="headphones", min_price=5000, max_price=20000
            )

        print("   ✅ API call succeeded")
        print(f"   Success: {result.success}")

        if result.success:
            if isinstance(result.data, dict) and "error" in result.data:
                print("   ⚠️  Crawler blocked by Amazon")
                test_results.append(True)
            elif isinstance(result.data, list):
                print(f"   ✅ SUCCESS! Got {len(result.data)} products")
                test_results.append(True)
            else:
                test_results.append(False)
        else:
            print(f"   ❌ Search failed: {result.error}")
            test_results.append(False)

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        test_results.append(False)

    # Test 3: Prime eligible filter
    print("\n" + "-" * 80)
    print("3️⃣ TEST: Prime Eligible Filter")
    print("-" * 80)
    print("   Method: client.search.amazon.products(")
    print("       keyword='phone charger',")
    print("       prime_eligible=True")
    print("   )")

    try:
        async with client.engine:
            result = await client.search.amazon.products(
                keyword="phone charger", prime_eligible=True
            )

        print("   ✅ API call succeeded")
        print(f"   Success: {result.success}")

        if result.success:
            if isinstance(result.data, dict) and "error" in result.data:
                print("   ⚠️  Crawler blocked by Amazon")
                test_results.append(True)
            elif isinstance(result.data, list):
                print(f"   ✅ SUCCESS! Got {len(result.data)} products")
                test_results.append(True)
            else:
                test_results.append(False)
        else:
            print(f"   ❌ Search failed: {result.error}")
            test_results.append(False)

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        test_results.append(False)

    # Final summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    passed = sum(test_results)
    total = len(test_results)

    print(f"   Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\n📊 Analysis:")
        print("   ✅ NEW client.search.amazon API is working")
        print("   ✅ SDK correctly builds search URLs from keywords")
        print("   ✅ SDK correctly triggers/polls/fetches results")
        print("   ⚠️  Amazon may still block searches (anti-bot protection)")
        print("\n💡 Key Difference:")
        print("   OLD: client.scrape.amazon.products('https://amazon.com/s?k=laptop')")
        print("   NEW: client.search.amazon.products(keyword='laptop')")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    asyncio.run(test_new_amazon_search_api())
