#!/usr/bin/env python3
"""Test Facebook scraper to verify API fetches data correctly.

How to run manually:
    python tests/enes/facebook.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def test_facebook_posts_by_profile():
    """Test Facebook posts by profile scraping."""

    print("=" * 60)
    print("FACEBOOK SCRAPER TEST - Posts by Profile")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.facebook
        async with scraper.engine:
            print("\n👤 Testing Facebook posts by profile...")
            print("📍 Profile URL: https://www.facebook.com/facebook")
            print("📋 Parameters: num_of_posts=5")

            try:
                result = await scraper.posts_by_profile(
                    url="https://www.facebook.com/facebook", num_of_posts=5, timeout=240
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} posts:")
                        for i, post in enumerate(result.data[:3], 1):
                            print(f"\n   Post {i}:")
                            print(
                                f"   - Text: {post.get('text', 'N/A')[:60]}..."
                                if post.get("text")
                                else "   - Text: N/A"
                            )
                            print(f"   - Likes: {post.get('likes', 'N/A')}")
                            print(f"   - Comments: {post.get('comments', 'N/A')}")
                            print(f"   - Shares: {post.get('shares', 'N/A')}")
                    elif isinstance(result.data, dict):
                        print("\n✅ Got post data:")
                        print(f"   - Text: {result.data.get('text', 'N/A')[:60]}...")
                        print(f"   - Likes: {result.data.get('likes', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No post data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_facebook_posts_by_group():
    """Test Facebook posts by group scraping."""

    print("\n\n" + "=" * 60)
    print("FACEBOOK SCRAPER TEST - Posts by Group")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.facebook
        async with scraper.engine:
            print("\n🏢 Testing Facebook posts by group...")
            print("📍 Group URL: https://www.facebook.com/groups/example")
            print("📋 Parameters: num_of_posts=5")

            try:
                result = await scraper.posts_by_group(
                    url="https://www.facebook.com/groups/example", num_of_posts=5, timeout=240
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} posts:")
                        for i, post in enumerate(result.data[:3], 1):
                            print(f"\n   Post {i}:")
                            print(
                                f"   - Text: {post.get('text', 'N/A')[:60]}..."
                                if post.get("text")
                                else "   - Text: N/A"
                            )
                            print(f"   - Author: {post.get('author', 'N/A')}")
                            print(f"   - Likes: {post.get('likes', 'N/A')}")
                    elif isinstance(result.data, dict):
                        print("\n✅ Got post data")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No post data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_facebook_posts_by_url():
    """Test Facebook specific post scraping."""

    print("\n\n" + "=" * 60)
    print("FACEBOOK SCRAPER TEST - Post by URL")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.facebook
        async with scraper.engine:
            print("\n📄 Testing Facebook specific post...")
            print("📍 Post URL: https://www.facebook.com/facebook/posts/123456789")

            try:
                result = await scraper.posts_by_url(
                    url="https://www.facebook.com/facebook/posts/123456789", timeout=240
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    print("\n✅ Got post data:")
                    if isinstance(result.data, dict):
                        print(
                            f"   - Text: {result.data.get('text', 'N/A')[:60]}..."
                            if result.data.get("text")
                            else "   - Text: N/A"
                        )
                        print(f"   - Likes: {result.data.get('likes', 'N/A')}")
                        print(f"   - Comments: {result.data.get('comments', 'N/A')}")
                        print(f"   - Shares: {result.data.get('shares', 'N/A')}")
                        print(f"   - Posted: {result.data.get('posted_date', 'N/A')}")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No post data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_facebook_comments():
    """Test Facebook comments scraping."""

    print("\n\n" + "=" * 60)
    print("FACEBOOK SCRAPER TEST - Comments")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.facebook
        async with scraper.engine:
            print("\n💬 Testing Facebook comments...")
            print("📍 Post URL: https://www.facebook.com/facebook/posts/123456789")
            print("📋 Parameters: num_of_comments=10")

            try:
                result = await scraper.comments(
                    url="https://www.facebook.com/facebook/posts/123456789",
                    num_of_comments=10,
                    timeout=240,
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} comments:")
                        for i, comment in enumerate(result.data[:3], 1):
                            print(f"\n   Comment {i}:")
                            print(
                                f"   - Text: {comment.get('text', 'N/A')[:60]}..."
                                if comment.get("text")
                                else "   - Text: N/A"
                            )
                            print(f"   - Author: {comment.get('author', 'N/A')}")
                            print(f"   - Likes: {comment.get('likes', 'N/A')}")
                    elif isinstance(result.data, dict):
                        comments = result.data.get("comments", [])
                        print(f"\n✅ Got {len(comments)} comments")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No comments data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


async def test_facebook_reels():
    """Test Facebook reels scraping."""

    print("\n\n" + "=" * 60)
    print("FACEBOOK SCRAPER TEST - Reels")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        scraper = client.scrape.facebook
        async with scraper.engine:
            print("\n🎥 Testing Facebook reels...")
            print("📍 Profile URL: https://www.facebook.com/facebook")
            print("📋 Parameters: num_of_posts=5")

            try:
                result = await scraper.reels(
                    url="https://www.facebook.com/facebook", num_of_posts=5, timeout=240
                )

                print("\n✅ API call succeeded")
                print(f"⏱️  Elapsed: {result.elapsed_ms():.2f}ms" if result.elapsed_ms() else "")

                print("\n📊 Result analysis:")
                print(f"   - result.success: {result.success}")
                print(f"   - result.data type: {type(result.data)}")

                if result.data:
                    if isinstance(result.data, list):
                        print(f"\n✅ Got {len(result.data)} reels:")
                        for i, reel in enumerate(result.data[:3], 1):
                            print(f"\n   Reel {i}:")
                            print(
                                f"   - Text: {reel.get('text', 'N/A')[:60]}..."
                                if reel.get("text")
                                else "   - Text: N/A"
                            )
                            print(f"   - Views: {reel.get('views', 'N/A')}")
                            print(f"   - Likes: {reel.get('likes', 'N/A')}")
                    elif isinstance(result.data, dict):
                        print("\n✅ Got reel data")
                    else:
                        print(f"   Data: {result.data}")
                else:
                    print("\n❌ No reels data returned")

            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback

                traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Facebook Scraper Tests\n")
    asyncio.run(test_facebook_posts_by_profile())
    asyncio.run(test_facebook_posts_by_group())
    asyncio.run(test_facebook_posts_by_url())
    asyncio.run(test_facebook_comments())
    asyncio.run(test_facebook_reels())
    print("\n" + "=" * 60)
    print("✅ Facebook tests completed")
    print("=" * 60)
