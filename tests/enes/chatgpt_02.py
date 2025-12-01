#!/usr/bin/env python3
"""Test ChatGPT scraper functionality.

Tests the ChatGPT prompt-based interface and verifies it works correctly.

How to run manually:
    python probe_tests/test_07_chatgpt.py
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brightdata import BrightDataClient


async def test_chatgpt():
    """Test ChatGPT functionality."""

    print("Testing ChatGPT Scraper")
    print("=" * 60)

    # Initialize client
    client = BrightDataClient()

    print(f"\n📍 Using bearer token: {client.token[:20]}...")

    # Initialize engine context - ALL operations must be within this context
    async with client.engine:

        # Test 1: Basic single prompt
        print("\n1. Testing basic single prompt...")
        try:
            prompt = "What is 2+2?"
            print(f"   Prompt: '{prompt}'")
            print("   Web search: False")
            print("   Country: US (default)")

            scraper = client.scrape.chatgpt
            result = await scraper.prompt_async(prompt=prompt, web_search=False, poll_timeout=60)

            if result.success:
                print("   ✅ Prompt successful!")
                print(f"   Data type: {type(result.data)}")
                if result.elapsed_ms():
                    print(f"   Elapsed: {result.elapsed_ms():.2f}ms")
                if result.cost:
                    print(f"   Cost: ${result.cost:.6f}")

                # Show response
                if result.data and len(result.data) > 0:
                    response = result.data[0]
                    print("\n   Response:")
                    print(f"   - Answer: {response.get('answer_text', 'N/A')[:100]}...")
                    print(f"   - Model: {response.get('model', 'N/A')}")
                    print(f"   - Country: {response.get('country', 'N/A')}")
                else:
                    print("   ⚠️  No response data")
            else:
                print(f"   ❌ Prompt failed: {result.error}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Prompt with web search
        print("\n2. Testing prompt with web search...")
        try:
            prompt = "What are the latest AI developments in 2024?"
            print(f"   Prompt: '{prompt}'")
            print("   Web search: True")
            print("   Country: US")

            result = await scraper.prompt_async(
                prompt=prompt, country="us", web_search=True, poll_timeout=90
            )

            if result.success:
                print("   ✅ Web search prompt successful!")
                print(f"   Results count: {len(result.data) if result.data else 0}")

                if result.data and len(result.data) > 0:
                    response = result.data[0]
                    print(f"   - Answer preview: {response.get('answer_text', 'N/A')[:150]}...")
                    print(f"   - Web search used: {response.get('web_search_triggered', False)}")
            else:
                print(f"   ❌ Failed: {result.error}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Batch prompts
        print("\n3. Testing batch prompts...")
        try:
            prompts = ["What is Python in one sentence?", "What is JavaScript in one sentence?"]
            print(f"   Prompts: {prompts}")
            print("   Countries: ['us', 'us']")

            result = await scraper.prompts_async(
                prompts=prompts,
                countries=["us", "us"],
                web_searches=[False, False],
                poll_timeout=120,
            )

            if result.success:
                print("   ✅ Batch prompts successful!")
                print(f"   Responses: {len(result.data) if result.data else 0}")

                if result.data:
                    for i, response in enumerate(result.data[:2], 1):
                        print(f"\n   Response {i}:")
                        print(f"   - Prompt: {response.get('input', {}).get('prompt', 'N/A')}")
                        print(f"   - Answer: {response.get('answer_text', 'N/A')[:100]}...")
                        print(f"   - Country: {response.get('country', 'N/A')}")
            else:
                print(f"   ❌ Failed: {result.error}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 4: Follow-up prompt (additional_prompt)
        print("\n4. Testing follow-up prompt...")
        try:
            prompt = "What is machine learning?"
            follow_up = "Can you give a simple example?"
            print(f"   Initial prompt: '{prompt}'")
            print(f"   Follow-up: '{follow_up}'")

            result = await scraper.prompt_async(
                prompt=prompt, additional_prompt=follow_up, web_search=False, poll_timeout=90
            )

            if result.success:
                print("   ✅ Follow-up prompt successful!")

                if result.data and len(result.data) > 0:
                    response = result.data[0]
                    print(f"   - Combined answer: {response.get('answer_text', 'N/A')[:200]}...")
            else:
                print(f"   ❌ Failed: {result.error}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 5: Verify ChatGPT doesn't support URL scraping
        print("\n5. Verifying URL scraping is disabled...")
        try:
            # This should raise NotImplementedError
            await scraper.scrape_async("https://example.com")
            print("   ❌ scrape_async() should have raised NotImplementedError")
        except NotImplementedError as e:
            print("   ✅ Correctly raises NotImplementedError")
            print(f"   - Message: {str(e)[:60]}...")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")

        # Test 6: Check ChatGPT-specific attributes
        print("\n6. Checking ChatGPT-specific configuration...")
        try:
            print(f"   Dataset ID: {scraper.DATASET_ID}")
            print(f"   Platform name: {scraper.PLATFORM_NAME}")
            print(f"   Min poll timeout: {scraper.MIN_POLL_TIMEOUT}s")
            print(f"   Cost per record: ${scraper.COST_PER_RECORD}")

            # Verify these are ChatGPT-specific values
            checks = [
                scraper.DATASET_ID == "gd_m7aof0k82r803d5bjm",
                scraper.PLATFORM_NAME == "chatgpt",
                scraper.COST_PER_RECORD == 0.005,  # ChatGPT is more expensive
            ]

            if all(checks):
                print("   ✅ All ChatGPT-specific attributes correct")
            else:
                print("   ⚠️  Some attributes don't match expected values")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 7: Manual trigger/status/fetch workflow
        print("\n7. Testing manual trigger/status/fetch...")
        try:
            prompt = "What is 1+1?"
            print(f"   Prompt: '{prompt}'")

            # Trigger only
            job = await scraper.prompt_trigger_async(prompt=prompt)
            print(f"   ✅ Triggered job: {job.snapshot_id}")

            # Check status
            status = await scraper.prompt_status_async(job.snapshot_id)
            print(f"   Initial status: {status}")

            # Poll until ready
            max_attempts = 30
            for attempt in range(max_attempts):
                status = await scraper.prompt_status_async(job.snapshot_id)
                if status == "ready":
                    print(f"   Status ready after {attempt + 1} checks")
                    break
                elif status == "error":
                    print("   ❌ Job failed with error status")
                    break
                await asyncio.sleep(2)

            # Fetch results
            if status == "ready":
                data = await scraper.prompt_fetch_async(job.snapshot_id)
                print("   ✅ Fetched data successfully")
                if data and len(data) > 0:
                    print(f"   - Answer: {data[0].get('answer_text', 'N/A')[:100]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 40)
    print(
        """
ChatGPT Scraper Configuration:
- Dataset ID: gd_m7aof0k82r803d5bjm
- Platform: chatgpt
- Cost per prompt: $0.005
- Default timeout: 120s (longer for AI responses)

Key differences from regular scrapers:
1. Uses prompt/prompts methods instead of scrape
2. Requires prompt parameter, not URLs
3. Supports web_search and additional_prompt options
4. Higher cost per operation
5. Longer response times

If getting errors:
1. Check API token is valid
2. Verify account has ChatGPT access enabled
3. Check account balance for ChatGPT operations
"""
    )


if __name__ == "__main__":
    asyncio.run(test_chatgpt())
