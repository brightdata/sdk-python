#!/usr/bin/env python3
"""
Interactive CLI demo for BrightData SDK.

Demonstrates all implemented features:
- Client initialization & connection testing
- Generic web scraping (Web Unlocker)
- Amazon scraping (products, reviews, sellers)
- LinkedIn scraping & search (posts, jobs, profiles, companies)
- ChatGPT scraping & search
- SERP API (Google, Bing, Yandex)
- Batch operations
- Sync vs async modes
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[OK] Loaded environment from: {env_file}")
    else:
        print("[WARN] No .env file found, using system environment variables")
except ImportError:
    print("[WARN] python-dotenv not installed")

from brightdata import BrightDataClient
from brightdata.scrapers import get_registered_platforms

print("=" * 80)
print("BRIGHTDATA SDK - COMPREHENSIVE INTERACTIVE DEMO")
print("=" * 80)
print()

# ============================================================================
# Step 1: Initialize Client
# ============================================================================

print("Step 1: Initialize Client")
print("-" * 80)

try:
    client = BrightDataClient()
    print(f"[OK] Client initialized: {client}")
    print(f"   Token: {client.token[:15]}...{client.token[-5:]}")
    print(f"   Timeout: {client.timeout}s")
    print(f"   Zones: unlocker={client.web_unlocker_zone}, serp={client.serp_zone}")
    print()
except Exception as e:
    print(f"[FAIL] Failed to initialize client: {e}")
    print()
    print("Make sure BRIGHTDATA_API_TOKEN is set in your environment")
    sys.exit(1)

# ============================================================================
# Step 2: Test Connection
# ============================================================================

print("Step 2: Test Connection & Account Info")
print("-" * 80)

async def test_connection():
    async with client:
        is_connected = await client.test_connection()
        
        if is_connected:
            print("[OK] Connection successful!")
            
            # Get account info
            info = await client.get_account_info()
            print(f"   Customer ID: {info.get('customer_id', 'N/A')}")
            print(f"   Zones: {info['zone_count']}")
            print(f"   Active zones:")
            for zone in info['zones'][:5]:
                zone_name = zone.get('name', 'unknown')
                print(f"     - {zone_name}")
            if info['zone_count'] > 5:
                print(f"     ... and {info['zone_count'] - 5} more")
            print()
            return True
        else:
            print("[FAIL] Connection failed")
            print()
            return False

connected = asyncio.run(test_connection())

if not connected:
    print("[WARN] Cannot connect to API. Continuing with limited demo...")
    print()

# ============================================================================
# Step 3: Show Complete API Structure
# ============================================================================

print("Step 3: Complete API Structure")
print("-" * 80)

platforms = get_registered_platforms()
print(f"[OK] {len(platforms)} platforms registered: {', '.join(platforms)}")
print()

print("CLIENT.SCRAPE.* (URL-based extraction):")
print("   • generic.url(url)")
print("   • amazon.products(url, sync, timeout)")
print("   • amazon.reviews(url, pastDays, keyWord, numOfReviews, sync, timeout)")
print("   • amazon.sellers(url, sync, timeout)")
print("   • linkedin.posts(url, sync, timeout)")
print("   • linkedin.jobs(url, sync, timeout)")
print("   • linkedin.profiles(url, sync, timeout)")
print("   • linkedin.companies(url, sync, timeout)")
print()

print("CLIENT.SEARCH.* (Parameter-based discovery):")
print("   • google(query, location, language, num_results)")
print("   • bing(query, location, language)")
print("   • yandex(query, location, language)")
print("   • linkedin.posts(profile_url, start_date, end_date)")
print("   • linkedin.profiles(firstName, lastName)")
print("   • linkedin.jobs(keyword, location, ...11 filters)")
print("   • chatGPT(prompt, country, secondaryPrompt, webSearch, sync)")
print()

# ============================================================================
# Step 4: Test Generic Web Scraper
# ============================================================================

print("Step 4: Generic Web Scraper Demo")
print("-" * 80)
print("Scraping https://httpbin.org/json (test URL)...")

try:
    result = client.scrape_url("https://httpbin.org/json")
    
    if result.success:
        print("[OK] Generic scrape successful!")
        print(f"   URL: {result.url}")
        print(f"   Status: {result.status}")
        print(f"   Domain: {result.root_domain}")
        print(f"   Size: {result.html_char_size:,} chars")
        print(f"   Time: {result.elapsed_ms():.2f}ms")
        print(f"   Data preview: {str(result.data)[:150]}...")
    else:
        print(f"[FAIL] Failed: {result.error}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

print()

# ============================================================================
# Interactive Menu
# ============================================================================

print("Interactive Testing Menu")
print("=" * 80)
print()

def show_menu():
    """Display interactive menu."""
    print("\nWhat would you like to test?")
    print()
    print("  SCRAPING (URL-based):")
    print("    1. Generic web scraping (httpbin.org)")
    print("    2. Amazon products (URL)")
    print("    3. Amazon reviews (URL + filters)")
    print("    4. LinkedIn profiles (URL)")
    print("    5. LinkedIn jobs (URL)")
    print()
    print("  SEARCH (Discovery):")
    print("    6. Google search (SERP)")
    print("    7. LinkedIn job search (keyword)")
    print("    8. LinkedIn profile search (name)")
    print("    9. ChatGPT prompt")
    print()
    print("  ADVANCED:")
    print("   10. Batch scraping (multiple URLs)")
    print("   11. Async vs sync mode comparison")
    print("   12. Show complete interface reference")
    print()
    print("    0. Exit")
    print()

def test_generic_scrape():
    """Test generic web scraping."""
    url = input("Enter URL to scrape (or press Enter for httpbin.org/html): ").strip()
    url = url or "https://httpbin.org/html"
    
    print(f"\nScraping: {url}")
    result = client.scrape_url(url)
    
    if result.success:
        print(f"[OK] Success!")
        print(f"   Status: {result.status}")
        print(f"   Size: {result.html_char_size} chars")
        print(f"   Time: {result.elapsed_ms():.2f}ms")
        print(f"   Data preview: {str(result.data)[:200]}...")
    else:
        print(f"[FAIL] Failed: {result.error}")

def test_amazon_products():
    """Test Amazon product scraping (URL-based)."""
    url = input("Enter Amazon product URL (e.g., https://amazon.com/dp/B123): ").strip()
    if not url:
        print("[FAIL] URL required")
        return
    
    print(f"\nScraping Amazon product: {url}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.scrape.amazon.products(url=url, timeout=240)
        
        if result.success:
            print(f"[OK] Success!")
            if isinstance(result.data, dict):
                print(f"   Title: {result.data.get('title', 'N/A')[:60]}")
                print(f"   Price: {result.data.get('price', 'N/A')}")
                print(f"   Rating: {result.data.get('rating', 'N/A')}")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
            print(f"   Time: {result.elapsed_ms():.2f}ms")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_amazon_reviews():
    """Test Amazon reviews scraping with filters."""
    url = input("Enter Amazon product URL: ").strip()
    if not url:
        print("[FAIL] URL required")
        return
    
    print("\nOptional filters:")
    past_days = input("  Past days (or Enter to skip): ").strip()
    keyword = input("  Keyword filter (or Enter to skip): ").strip()
    num_reviews = input("  Number of reviews (or Enter for default): ").strip()
    
    print(f"\nScraping reviews from: {url}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.scrape.amazon.reviews(
            url=url,
            pastDays=int(past_days) if past_days else None,
            keyWord=keyword if keyword else None,
            numOfReviews=int(num_reviews) if num_reviews else None,
            timeout=240
        )
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Reviews: {result.row_count}")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_linkedin_profiles():
    """Test LinkedIn profile scraping (URL-based)."""
    url = input("Enter LinkedIn profile URL (e.g., https://linkedin.com/in/johndoe): ").strip()
    if not url:
        print("[FAIL] URL required")
        return
    
    print(f"\nScraping LinkedIn profile: {url}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.scrape.linkedin.profiles(url=url, timeout=180)
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
            print(f"   Time: {result.elapsed_ms():.2f}ms")
            if isinstance(result.data, dict):
                print(f"   Name: {result.data.get('name', 'N/A')}")
                print(f"   Headline: {result.data.get('headline', 'N/A')[:60]}")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_linkedin_jobs_url():
    """Test LinkedIn job scraping (URL-based)."""
    url = input("Enter LinkedIn job URL (e.g., https://linkedin.com/jobs/view/123): ").strip()
    if not url:
        print("[FAIL] URL required")
        return
    
    print(f"\nScraping LinkedIn job: {url}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.scrape.linkedin.jobs(url=url, timeout=180)
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_google_search():
    """Test Google SERP search."""
    query = input("Enter search query: ").strip()
    if not query:
        print("[FAIL] Query required")
        return
    
    location = input("Enter location (e.g., 'United States', or Enter for default): ").strip()
    
    print(f"\nSearching Google: {query}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.search.google(
            query=query,
            location=location if location else None,
            num_results=10
        )
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Total found: {result.total_found:,}" if result.total_found else "   Total: N/A")
            print(f"   Results returned: {len(result.data)}")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
            
            if result.data:
                print("\n   Top 3 results:")
                for i, item in enumerate(result.data[:3], 1):
                    print(f"   {i}. {item.get('title', 'N/A')[:60]}")
                    print(f"      {item.get('url', 'N/A')[:70]}")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_linkedin_job_search():
    """Test LinkedIn job search (discovery)."""
    keyword = input("Enter job keyword (e.g., 'python developer'): ").strip()
    location = input("Enter location (e.g., 'New York', or Enter to skip): ").strip()
    remote = input("Remote only? (y/n, or Enter to skip): ").strip().lower()
    
    if not keyword:
        print("[FAIL] Keyword required")
        return
    
    print(f"\nSearching LinkedIn jobs: {keyword}")
    if location:
        print(f"Location: {location}")
    if remote == 'y':
        print("Remote: Yes")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.search.linkedin.jobs(
            keyword=keyword,
            location=location if location else None,
            remote=True if remote == 'y' else None,
            timeout=180
        )
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Jobs found: {result.row_count}")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_linkedin_profile_search():
    """Test LinkedIn profile search by name."""
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name (or Enter to skip): ").strip()
    
    if not first_name:
        print("[FAIL] First name required")
        return
    
    print(f"\nSearching LinkedIn profiles: {first_name} {last_name}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.search.linkedin.profiles(
            firstName=first_name,
            lastName=last_name if last_name else None,
            timeout=180
        )
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Profiles found: {result.row_count}")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_chatgpt_search():
    """Test ChatGPT search."""
    prompt = input("Enter prompt for ChatGPT: ").strip()
    
    if not prompt:
        print("[FAIL] Prompt required")
        return
    
    web_search = input("Enable web search? (y/n): ").strip().lower()
    
    print(f"\nSending prompt to ChatGPT: {prompt}")
    if web_search == 'y':
        print("Web search: Enabled")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        result = client.search.chatGPT.chatGPT(
            prompt=prompt,
            webSearch=True if web_search == 'y' else False,
            timeout=240
        )
        
        if result.success:
            print(f"[OK] Success!")
            print(f"   Cost: ${result.cost:.4f}" if result.cost else "   Cost: N/A")
            print(f"   Response preview: {str(result.data)[:200]}...")
        else:
            print(f"[FAIL] Failed: {result.error}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_batch_scraping():
    """Test batch scraping (multiple URLs)."""
    print("\nBatch Scraping Demo")
    print("Enter 3 URLs to scrape concurrently:")
    
    urls = []
    for i in range(3):
        url = input(f"  URL {i+1} (or Enter for default): ").strip()
        urls.append(url or f"https://httpbin.org/html")
    
    print(f"\nScraping {len(urls)} URLs concurrently...")
    
    try:
        import time
        start = time.time()
        
        results = client.scrape_url(urls)
        
        elapsed = time.time() - start
        
        print(f"[OK] Completed in {elapsed:.2f}s")
        print()
        
        for i, result in enumerate(results, 1):
            status = "[OK]" if result.success else "[FAIL]"
            print(f"{status} {i}. {result.url[:50]}")
            print(f"   Status: {result.status}, Size: {result.html_char_size} chars")
        
        print(f"\nTotal time: {elapsed:.2f}s")
        print(f"Average per URL: {elapsed/len(urls):.2f}s")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def test_sync_vs_async():
    """Test sync vs async mode comparison."""
    url = input("Enter URL (or Enter for default): ").strip()
    url = url or "https://httpbin.org/html"
    
    print(f"\nComparing sync vs async modes for: {url}")
    print("[WARN] This will use Bright Data credits!")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled")
        return
    
    try:
        import time
        
        # Test sync mode
        print("\n1. Sync mode (immediate response):")
        start = time.time()
        result_sync = client.scrape_url(url)
        sync_time = time.time() - start
        
        print(f"   Time: {sync_time:.2f}s")
        print(f"   Success: {result_sync.success}")
        
        # Test async mode  
        print("\n2. Async mode (with polling):")
        print("   All scrapers use standard async workflow (trigger/poll/fetch)")
        print("   Sync methods are simple wrappers around async methods")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")

def show_complete_interface():
    """Show complete client interface reference."""
    print("\n" + "=" * 80)
    print("COMPLETE CLIENT INTERFACE REFERENCE")
    print("=" * 80)
    print()
    
    print("INITIALIZATION:")
    print("  client = BrightDataClient()  # Auto-loads from environment")
    print("  client = BrightDataClient(token='your_token', timeout=60)")
    print()
    
    print("CONNECTION:")
    print("  is_valid = await client.test_connection()")
    print("  info = await client.get_account_info()")
    print()
    
    print("SCRAPE (URL-based extraction):")
    print("  client.scrape_url(url)")
    print("  client.scrape.amazon.products(url, timeout=240)")
    print("  client.scrape.amazon.reviews(url, pastDays, keyWord, numOfReviews, timeout=240)")
    print("  client.scrape.amazon.sellers(url, timeout=240)")
    print("  client.scrape.linkedin.posts(url, sync, timeout)")
    print("  client.scrape.linkedin.jobs(url, sync, timeout)")
    print("  client.scrape.linkedin.profiles(url, sync, timeout)")
    print("  client.scrape.linkedin.companies(url, sync, timeout)")
    print()
    
    print("SEARCH (Parameter-based discovery):")
    print("  client.search.google(query, location, language, num_results)")
    print("  client.search.bing(query, location)")
    print("  client.search.yandex(query, location)")
    print("  client.search.linkedin.posts(profile_url, start_date, end_date)")
    print("  client.search.linkedin.profiles(firstName, lastName)")
    print("  client.search.linkedin.jobs(keyword, location, country, ...)")
    print("  client.search.chatGPT.chatGPT(prompt, country, secondaryPrompt, webSearch, sync)")
    print()
    
    print("RESULT OBJECTS:")
    print("  result.success       # bool")
    print("  result.data          # Any - scraped/searched data")
    print("  result.error         # str | None")
    print("  result.cost          # float | None - USD")
    print("  result.elapsed_ms()  # float - milliseconds")
    print("  result.to_json()     # str - JSON serialization")
    print("  result.save_to_file('output.json')")
    print()
    
    print("ASYNC USAGE:")
    print("  async with BrightDataClient() as client:")
    print("      result = await client.scrape_url(url)")
    print()

# Interactive loop
while True:
    try:
        show_menu()
        choice = input("Enter choice (0-12): ").strip()
        print()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            test_generic_scrape()
        elif choice == "2":
            test_amazon_products()
        elif choice == "3":
            test_amazon_reviews()
        elif choice == "4":
            test_linkedin_profiles()
        elif choice == "5":
            test_linkedin_jobs_url()
        elif choice == "6":
            test_google_search()
        elif choice == "7":
            test_linkedin_job_search()
        elif choice == "8":
            test_linkedin_profile_search()
        elif choice == "9":
            test_chatgpt_search()
        elif choice == "10":
            test_batch_scraping()
        elif choice == "11":
            test_sync_vs_async()
        elif choice == "12":
            show_complete_interface()
        else:
            print("[FAIL] Invalid choice. Please enter 0-12.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        break
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 80)
print("Demo completed! For more info, see README.md")
print("=" * 80)
