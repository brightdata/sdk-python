#!/usr/bin/env python3
"""Test Instagram scraper and search to verify API fetches data correctly.

How to run manually:
    python tests/enes/instagram.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def test_instagram_profiles():
    """Test Instagram profile scraping."""

    print("=" * 60)
    print("INSTAGRAM SCRAPER TEST - Profiles")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.instagram
        async with scraper.engine:
            print("\n👤 Testing Instagram profile scraping...")
            print("📍 Profile URL: https://www.instagram.com/instagram")

            try:
                result = await scraper.profiles_async(
                    url="https://www.instagram.com/instagram", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got profile data:")
                    if isinstance(result.data, dict):
                        print(f"   - Username: {result.data.get('username', 'N/A')}")
                        print(f"   - Full Name: {result.data.get('full_name', 'N/A')}")
                        print(f"   - Followers: {result.data.get('followers', 'N/A')}")
                        print(f"   - Following: {result.data.get('following', 'N/A')}")
                        print(f"   - Posts: {result.data.get('posts_count', 'N/A')}")
                        print(f"   - Bio: {result.data.get('bio', 'N/A')[:60]}...")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No profile data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_instagram_posts():
    """Test Instagram post scraping."""

    print("\n\n" + "=" * 60)
    print("INSTAGRAM SCRAPER TEST - Posts")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.instagram
        async with scraper.engine:
            print("\n📸 Testing Instagram post scraping...")
            print("📍 Post URL: https://www.instagram.com/p/C9z9z9z9z9z")

            try:
                result = await scraper.posts_async(
                    url="https://www.instagram.com/p/C9z9z9z9z9z", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got post data:")
                    if isinstance(result.data, dict):
                        print(f"   - Caption: {result.data.get('caption', 'N/A')[:60]}...")
                        print(f"   - Likes: {result.data.get('likes', 'N/A')}")
                        print(f"   - Comments: {result.data.get('comments_count', 'N/A')}")
                        print(f"   - Posted: {result.data.get('timestamp', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No post data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_instagram_reels():
    """Test Instagram reel scraping."""

    print("\n\n" + "=" * 60)
    print("INSTAGRAM SCRAPER TEST - Reels")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.instagram
        async with scraper.engine:
            print("\n🎥 Testing Instagram reel scraping...")
            print("📍 Reel URL: https://www.instagram.com/reel/ABC123")

            try:
                result = await scraper.reels_async(
                    url="https://www.instagram.com/reel/ABC123", timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got reel data:")
                    if isinstance(result.data, dict):
                        print(f"   - Caption: {result.data.get('caption', 'N/A')[:60]}...")
                        print(f"   - Likes: {result.data.get('likes', 'N/A')}")
                        print(f"   - Views: {result.data.get('views', 'N/A')}")
                        print(f"   - Comments: {result.data.get('comments_count', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No reel data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_instagram_search_posts():
    """Test Instagram post search/discovery."""

    print("\n\n" + "=" * 60)
    print("INSTAGRAM SEARCH TEST - Posts")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.search.instagram
        async with scraper.engine:
            print("\n🔍 Testing Instagram post search...")
            print("📋 Search: profile url, num_of_posts=10")

            try:
                result = await scraper.posts_async(
                    url="https://www.instagram.com/instagram", num_of_posts=10, timeout=180
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} post results:")
                        for i, post in enumerate(result.data[:3], 1):
                            print(f"\n   Post {i}:")
                            print(f"   - Caption: {post.get('caption', 'N/A')[:50]}...")
                            print(f"   - Likes: {post.get('likes', 'N/A')}")
                            print(f"   - Comments: {post.get('comments_count', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No search results returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Instagram Scraper & Search Tests\n")
    asyncio.run(test_instagram_profiles())
    asyncio.run(test_instagram_posts())
    asyncio.run(test_instagram_reels())
    asyncio.run(test_instagram_search_posts())
    print("\n" + "=" * 60)
    print("✅ Instagram tests completed")
    print("=" * 60)
