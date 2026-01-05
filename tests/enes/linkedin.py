#!/usr/bin/env python3
"""Test LinkedIn scraper and search to verify API fetches data correctly.

How to run manually:
    python tests/enes/linkedin.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def test_linkedin_profiles():
    """Test LinkedIn profile scraping."""

    print("=" * 60)
    print("LINKEDIN SCRAPER TEST - Profiles")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.linkedin
        async with scraper.engine:
            print("\n👤 Testing LinkedIn profile scraping...")
            print("📍 Profile URL: https://www.linkedin.com/in/williamhgates")

            try:
                result = await scraper.profiles(
                    url="https://www.linkedin.com/in/williamhgates", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got profile data:")
                    if isinstance(result.data, dict):
                        print(f"   - Name: {result.data.get('name', 'N/A')}")
                        print(f"   - Headline: {result.data.get('headline', 'N/A')}")
                        print(f"   - Location: {result.data.get('location', 'N/A')}")
                        print(f"   - Connections: {result.data.get('connections', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No profile data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_linkedin_companies():
    """Test LinkedIn company scraping."""

    print("\n\n" + "=" * 60)
    print("LINKEDIN SCRAPER TEST - Companies")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.linkedin
        async with scraper.engine:
            print("\n🏢 Testing LinkedIn company scraping...")
            print("📍 Company URL: https://www.linkedin.com/company/microsoft")

            try:
                result = await scraper.companies(
                    url="https://www.linkedin.com/company/microsoft", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got company data:")
                    if isinstance(result.data, dict):
                        print(f"   - Name: {result.data.get('name', 'N/A')}")
                        print(f"   - Industry: {result.data.get('industry', 'N/A')}")
                        print(f"   - Size: {result.data.get('company_size', 'N/A')}")
                        print(f"   - Website: {result.data.get('website', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No company data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_linkedin_jobs():
    """Test LinkedIn job scraping."""

    print("\n\n" + "=" * 60)
    print("LINKEDIN SCRAPER TEST - Jobs")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.linkedin
        async with scraper.engine:
            print("\n💼 Testing LinkedIn job scraping...")
            print("📍 Job URL: https://www.linkedin.com/jobs/view/3787241244")

            try:
                result = await scraper.jobs(
                    url="https://www.linkedin.com/jobs/view/3787241244", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got job data:")
                    if isinstance(result.data, dict):
                        print(f"   - Title: {result.data.get('title', 'N/A')}")
                        print(f"   - Company: {result.data.get('company', 'N/A')}")
                        print(f"   - Location: {result.data.get('location', 'N/A')}")
                        print(f"   - Posted: {result.data.get('posted_date', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No job data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_linkedin_search_jobs():
    """Test LinkedIn job search."""

    print("\n\n" + "=" * 60)
    print("LINKEDIN SEARCH TEST - Jobs")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.search.linkedin
        async with scraper.engine:
            print("\n🔍 Testing LinkedIn job search...")
            print("📋 Search: keyword='python developer', location='New York'")

            try:
                result = await scraper.jobs(
                    keyword="python developer", location="New York", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")
                print(
                    f"   - result.status: {result.status if hasattr(result, 'status') else 'N/A'}"
                )
                print(f"   - result.error: {result.error if hasattr(result, 'error') else 'N/A'}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} job results:")
                        for i, job in enumerate(result.data[:3], 1):
                            print(f"\n   Job {i}:")
                            print(f"   - Title: {job.get('title', 'N/A')}")
                            print(f"   - Company: {job.get('company', 'N/A')}")
                            print(f"   - Location: {job.get('location', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No search results returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting LinkedIn Scraper & Search Tests\n")
    asyncio.run(test_linkedin_profiles())
    asyncio.run(test_linkedin_companies())
    asyncio.run(test_linkedin_jobs())
    asyncio.run(test_linkedin_search_jobs())
    print("\n" + "=" * 60)
    print("✅ LinkedIn tests completed")
    print("=" * 60)
