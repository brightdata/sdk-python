"""
Example: Manual Trigger/Poll/Fetch Interface

Demonstrates how to use the new trigger interface for manual control
over the scrape lifecycle: trigger -> status -> fetch.

Use cases:
- Start multiple scrapes concurrently
- Custom polling logic
- Save job IDs for later retrieval
- Optimize cost and timing

Run: python examples/11_trigger_interface.py
"""

import asyncio
import time
from brightdata import BrightDataClient


# ============================================================================
# Example 1: Basic Trigger/Poll/Fetch Pattern
# ============================================================================

async def example_basic_trigger():
    """Trigger a scrape, wait, and fetch results manually."""
    
    print("=" * 60)
    print("Example 1: Basic Trigger/Poll/Fetch")
    print("=" * 60)
    
    async with BrightDataClient() as client:
        amazon = client.scrape.amazon
        
        # Step 1: Trigger the scrape (returns immediately)
        print("\n🚀 Triggering Amazon product scrape...")
        job = await amazon.products_trigger(
            url="https://www.amazon.com/dp/B0CRMZHDG8"
        )
        print(f"✅ Job triggered: {job.snapshot_id}")
        
        # Step 2: Check status manually
        print("\n🔍 Checking job status...")
        status = await job.status()
        print(f"Status: {status}")
        
        # Step 3: Wait for completion (with custom timeout)
        print("\n⏳ Waiting for completion...")
        await job.wait(timeout=180, verbose=True)
        
        # Step 4: Fetch results
        print("\n📥 Fetching results...")
        data = await job.fetch()
        print(f"✅ Got {len(data) if isinstance(data, list) else 1} records")
        
        # Or use convenience method (wait + fetch + wrap in ScrapeResult)
        print("\n💡 Alternative: Use to_result_async()...")
        result = await job.to_result()
        print(f"Success: {result.success}")
        print(f"Cost: ${result.cost:.4f}")


# ============================================================================
# Example 2: Concurrent Scraping (Trigger Multiple, Fetch Later)
# ============================================================================

async def example_concurrent_scraping():
    """Trigger multiple scrapes concurrently, then fetch all."""
    
    print("\n\n" + "=" * 60)
    print("Example 2: Concurrent Scraping")
    print("=" * 60)
    
    async with BrightDataClient() as client:
        amazon = client.scrape.amazon
        
        # URLs to scrape
        urls = [
            "https://www.amazon.com/dp/B0CRMZHDG8",
            "https://www.amazon.com/dp/B09B9C8K3T",
            "https://www.amazon.com/dp/B0CX23V2ZK",
        ]
        
        # Step 1: Trigger all scrapes (non-blocking)
        print("\n🚀 Triggering multiple scrapes...")
        jobs = []
        for i, url in enumerate(urls, 1):
            job = await amazon.products_trigger(url=url)
            jobs.append(job)
            print(f"   [{i}/{len(urls)}] Triggered: {job.snapshot_id[:12]}...")
        
        print(f"\n✅ All {len(jobs)} jobs triggered!")
        
        # Step 2: Wait for all to complete
        print("\n⏳ Waiting for all jobs to complete...")
        results = []
        for i, job in enumerate(jobs, 1):
            print(f"   [{i}/{len(jobs)}] Waiting for job {job.snapshot_id[:12]}...")
            result = await job.to_result(timeout=180)
            results.append(result)
        
        # Step 3: Process all results
        print("\n📊 Results summary:")
        total_cost = sum(r.cost or 0 for r in results)
        successful = sum(1 for r in results if r.success)
        print(f"   - Successful: {successful}/{len(results)}")
        print(f"   - Total cost: ${total_cost:.4f}")
        print(f"   - Avg time: {sum(r.elapsed_ms() or 0 for r in results) / len(results):.0f}ms")


# ============================================================================
# Example 3: Custom Polling Logic
# ============================================================================

async def example_custom_polling():
    """Implement custom polling logic with your own intervals."""
    
    print("\n\n" + "=" * 60)
    print("Example 3: Custom Polling Logic")
    print("=" * 60)
    
    async with BrightDataClient() as client:
        amazon = client.scrape.amazon
        
        # Trigger the scrape
        print("\n🚀 Triggering scrape...")
        job = await amazon.products_trigger(
            url="https://www.amazon.com/dp/B0CRMZHDG8"
        )
        print(f"✅ Job ID: {job.snapshot_id}")
        
        # Custom polling with exponential backoff
        print("\n⏳ Custom polling with exponential backoff...")
        poll_interval = 2  # Start with 2 seconds
        max_interval = 20  # Max 20 seconds
        max_attempts = 30
        
        for attempt in range(max_attempts):
            status = await job.status()
            elapsed = time.time() - job.triggered_at.timestamp()
            
            print(f"   [{elapsed:.1f}s] Attempt {attempt + 1}: {status}")
            
            if status == "ready":
                print("✅ Job completed!")
                data = await job.fetch()
                print(f"📥 Got {len(data) if isinstance(data, list) else 1} records")
                break
            elif status == "error":
                print("❌ Job failed")
                break
            
            # Wait with exponential backoff
            await asyncio.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, max_interval)
        else:
            print("⏰ Timeout reached")


# ============================================================================
# Example 4: Save Job ID for Later Retrieval
# ============================================================================

async def example_save_and_resume():
    """Trigger a job, save the ID, and retrieve it later."""
    
    print("\n\n" + "=" * 60)
    print("Example 4: Save Job ID & Resume Later")
    print("=" * 60)
    
    async with BrightDataClient() as client:
        amazon = client.scrape.amazon
        
        # Phase 1: Trigger and save job ID
        print("\n📝 Phase 1: Trigger and save job ID...")
        job = await amazon.products_trigger(
            url="https://www.amazon.com/dp/B0CRMZHDG8"
        )
        snapshot_id = job.snapshot_id
        print(f"✅ Job triggered: {snapshot_id}")
        print(f"💾 Saved snapshot_id for later: {snapshot_id}")
        
        # Simulate doing other work...
        print("\n💤 Simulating other work (5 seconds)...")
        await asyncio.sleep(5)
        
        # Phase 2: Resume with saved snapshot_id
        print("\n🔄 Phase 2: Resume with saved snapshot_id...")
        print(f"📂 Loading snapshot_id: {snapshot_id}")
        
        # Check status using the snapshot_id directly
        status = await amazon.products_status(snapshot_id)
        print(f"Status: {status}")
        
        # Fetch if ready
        if status == "ready":
            data = await amazon.products_fetch(snapshot_id)
            print(f"✅ Fetched {len(data) if isinstance(data, list) else 1} records")
        else:
            print("⏳ Job not ready yet, would need to wait longer...")


# ============================================================================
# Example 5: Sync Usage (for non-async code)
# ============================================================================

def example_sync_usage():
    """Use trigger interface in synchronous code."""
    
    print("\n\n" + "=" * 60)
    print("Example 5: Sync Usage")
    print("=" * 60)
    
    client = BrightDataClient()
    amazon = client.scrape.amazon
    
    # Trigger (sync)
    print("\n🚀 Triggering scrape (sync)...")
    job = amazon.products_trigger(url="https://www.amazon.com/dp/B0CRMZHDG8")
    print(f"✅ Job ID: {job.snapshot_id}")
    
    # Check status (sync)
    print("\n🔍 Checking status (sync)...")
    status = job.status()
    print(f"Status: {status}")
    
    # Wait and fetch (sync)
    print("\n⏳ Waiting for completion (sync)...")
    result = job.to_result(timeout=180)
    print(f"Success: {result.success}")
    print(f"Cost: ${result.cost:.4f}")


# ============================================================================
# Run All Examples
# ============================================================================

if __name__ == "__main__":
    print("\n🚀 Trigger Interface Examples\n")
    
    # Run async examples
    asyncio.run(example_basic_trigger())
    asyncio.run(example_concurrent_scraping())
    asyncio.run(example_custom_polling())
    asyncio.run(example_save_and_resume())
    
    # Run sync example
    example_sync_usage()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)

