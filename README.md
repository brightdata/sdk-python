# Bright Data Python SDK 🐍

[![Tests](https://img.shields.io/badge/tests-502%2B%20passing-brightgreen)](https://github.com/brightdata/sdk-python)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/quality-enterprise--grade-gold)](https://github.com/brightdata/sdk-python)
[![Notebooks](https://img.shields.io/badge/jupyter-5%20notebooks-orange)](notebooks/)

Modern async-first Python SDK for [Bright Data](https://brightdata.com) APIs with **dataclass payloads**, **Jupyter notebooks**, comprehensive platform support, and **CLI tool** - built for data scientists and developers.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [📓 Jupyter Notebooks](#-jupyter-notebooks-new)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
  - [Authentication](#authentication)
  - [Simple Web Scraping](#simple-web-scraping)
  - [Using Dataclass Payloads](#using-dataclass-payloads-type-safe-)
  - [Pandas Integration](#pandas-integration-for-data-scientists-)
  - [Platform-Specific Scraping](#platform-specific-scraping)
  - [Search Engine Results (SERP)](#search-engine-results-serp)
  - [Async Usage](#async-usage)
- [🆕 What's New in v2.0.0](#-whats-new-in-v2-200)
- [🏗️ Architecture](#️-architecture)
- [📚 API Reference](#-api-reference)
  - [Client Initialization](#client-initialization)
  - [Connection Testing](#connection-testing)
  - [Zone Management](#zone-management)
  - [Result Objects](#result-objects)
- [🖥️ CLI Usage](#️-cli-usage)
- [🐼 Pandas Integration](#-pandas-integration)
- [🎨 Dataclass Payloads](#-dataclass-payloads)
- [🔧 Advanced Usage](#-advanced-usage)
- [🧪 Testing](#-testing)
- [🏛️ Design Philosophy](#️-design-philosophy)
- [📖 Documentation](#-documentation)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📊 Project Stats](#-project-stats)
- [📝 License](#-license)
- [🔗 Links](#-links)
- [💡 Examples](#-examples)
- [🎯 Roadmap](#-roadmap)
- [🙏 Acknowledgments](#-acknowledgments)
- [🌟 Why Choose This SDK?](#-why-choose-this-sdk)

---

## ✨ Features

### 🎯 **For Data Scientists**
- 📓 **5 Jupyter Notebooks** - Complete tutorials from quickstart to batch processing
- 🐼 **Pandas Integration** - Native DataFrame support with examples
- 📊 **Data Analysis Ready** - Built-in visualization, export to CSV/Excel
- 💰 **Cost Tracking** - Budget management and cost analytics
- 🔄 **Progress Bars** - tqdm integration for batch operations
- 💾 **Caching Support** - joblib integration for development

### 🏗️ **Core Features**
- 🚀 **Async-first architecture** with sync wrappers for compatibility
- 🎨 **Dataclass Payloads** - Runtime validation, IDE autocomplete, helper methods
- 🌐 **Web scraping** via Web Unlocker proxy service
- 🔍 **SERP API** - Google, Bing, Yandex search results
- 📦 **Platform scrapers** - LinkedIn, Amazon, ChatGPT, Facebook, Instagram
- 🎯 **Dual namespace** - `scrape` (URL-based) + `search` (discovery)
- 🖥️ **CLI Tool** - `brightdata` command for terminal usage

### 🛡️ **Enterprise Grade**
- 🔒 **100% type safety** - Dataclasses + TypedDict definitions
- ✅ **502+ comprehensive tests** - Unit, integration, and E2E
- ⚡ **Resource efficient** - Single shared AsyncEngine
- 🎨 **Rich result objects** - Timing, cost tracking, method tracking
- 🔐 **.env file support** - Automatic loading via python-dotenv
- 🛡️ **SSL error handling** - Helpful guidance for certificate issues
- 📊 **Function-level monitoring** - Track which SDK methods are used

---

## 📓 Jupyter Notebooks (NEW!)

Perfect for data scientists! Interactive tutorials with examples:

1. **[01_quickstart.ipynb](notebooks/01_quickstart.ipynb)** - Get started in 5 minutes [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brightdata/sdk-python/blob/main/notebooks/01_quickstart.ipynb)
2. **[02_pandas_integration.ipynb](notebooks/02_pandas_integration.ipynb)** - Work with DataFrames [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brightdata/sdk-python/blob/main/notebooks/02_pandas_integration.ipynb)
3. **[03_amazon_scraping.ipynb](notebooks/03_amazon_scraping.ipynb)** - Amazon deep dive [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brightdata/sdk-python/blob/main/notebooks/03_amazon_scraping.ipynb)
4. **[04_linkedin_jobs.ipynb](notebooks/04_linkedin_jobs.ipynb)** - Job market analysis [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brightdata/sdk-python/blob/main/notebooks/04_linkedin_jobs.ipynb)
5. **[05_batch_processing.ipynb](notebooks/05_batch_processing.ipynb)** - Scale to 1000s of URLs [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/brightdata/sdk-python/blob/main/notebooks/05_batch_processing.ipynb)

---

## 📦 Installation

```bash
pip install brightdata-sdk
```

Or install from source:

```bash
git clone https://github.com/brightdata/sdk-python.git
cd sdk-python
pip install -e .
```

---

## 🚀 Quick Start

### Authentication

Set your API token as an environment variable:

```bash
export BRIGHTDATA_API_TOKEN="your_api_token_here"
export BRIGHTDATA_CUSTOMER_ID="your_customer_id"  # Optional
```

Or use a `.env` file (automatically loaded):

```bash
# .env
BRIGHTDATA_API_TOKEN=your_api_token_here
BRIGHTDATA_CUSTOMER_ID=your_customer_id  # Optional
```

Or pass credentials directly:

```python
from brightdata import BrightDataClient

client = BrightDataClient(
    token="your_api_token",
    customer_id="your_customer_id"  # Optional
)
```

### Simple Web Scraping

```python
from brightdata import BrightDataClient

# Initialize client (auto-loads token from environment)
client = BrightDataClient()

# Scrape any website (sync wrapper)
result = client.scrape.generic.url("https://example.com")

if result.success:
print(f"Success: {result.success}")
print(f"Data: {result.data[:200]}...")
print(f"Time: {result.elapsed_ms():.2f}ms")
else:
    print(f"Error: {result.error}")
```

### Using Dataclass Payloads (Type-Safe ✨)

```python
from brightdata import BrightDataClient
from brightdata.payloads import AmazonProductPayload, LinkedInJobSearchPayload

client = BrightDataClient()

# Amazon with validated payload
payload = AmazonProductPayload(
    url="https://amazon.com/dp/B123456789",
    reviews_count=50  # Runtime validated!
)
print(f"ASIN: {payload.asin}")  # Helper property

result = client.scrape.amazon.products(**payload.to_dict())

# LinkedIn job search with validation
job_payload = LinkedInJobSearchPayload(
    keyword="python developer",
    location="New York",
    remote=True
)
print(f"Remote search: {job_payload.is_remote_search}")

jobs = client.search.linkedin.jobs(**job_payload.to_dict())
```

### Pandas Integration for Data Scientists 🐼

```python
import pandas as pd
from brightdata import BrightDataClient

client = BrightDataClient()

# Scrape multiple products
urls = ["https://amazon.com/dp/B001", "https://amazon.com/dp/B002"]
results = []

for url in urls:
    result = client.scrape.amazon.products(url=url)
    if result.success:
        results.append({
            'title': result.data.get('title'),
            'price': result.data.get('final_price'),
            'rating': result.data.get('rating'),
            'cost': result.cost
        })

# Convert to DataFrame
df = pd.DataFrame(results)
print(df.describe())

# Export to CSV
df.to_csv('products.csv', index=False)
```

### Platform-Specific Scraping

#### Amazon Products

```python
# Scrape specific product URLs
result = client.scrape.amazon.products(
    url="https://amazon.com/dp/B0CRMZHDG8",
    timeout=65
)

# Extract reviews with filters
result = client.scrape.amazon.reviews(
    url="https://amazon.com/dp/B0CRMZHDG8",
    pastDays=30,
    keyWord="quality",
    numOfReviews=100
)

# Scrape seller information
result = client.scrape.amazon.sellers(
    url="https://amazon.com/sp?seller=AXXXXXXXXX"
)

# NEW: Search Amazon by keyword and filters
result = client.search.amazon.products(
    keyword="laptop",
    min_price=50000,    # $500 in cents
    max_price=200000,   # $2000 in cents
    prime_eligible=True,
    condition="new"
)

# Search by category
result = client.search.amazon.products(
    keyword="wireless headphones",
    category="electronics"
)
```

#### LinkedIn Data

```python
# URL-based extraction
result = client.scrape.linkedin.profiles(
    url="https://linkedin.com/in/johndoe"
)

result = client.scrape.linkedin.jobs(
    url="https://linkedin.com/jobs/view/123456"
)

result = client.scrape.linkedin.companies(
    url="https://linkedin.com/company/microsoft"
)

result = client.scrape.linkedin.posts(
    url="https://linkedin.com/feed/update/..."
)

# Discovery/search operations
result = client.search.linkedin.jobs(
    keyword="python developer",
    location="New York",
    remote=True,
    experienceLevel="mid"
)

result = client.search.linkedin.profiles(
    firstName="John",
    lastName="Doe"
)

result = client.search.linkedin.posts(
    profile_url="https://linkedin.com/in/johndoe",
    start_date="2025-01-01",
    end_date="2025-12-31"
)
```

#### ChatGPT Interactions

```python
# Send single prompt to ChatGPT
result = client.scrape.chatgpt.prompt(
    prompt="Explain Python async programming",
    country="us",
    web_search=True
)

# Batch prompts
result = client.scrape.chatgpt.prompts(
    prompts=["What is Python?", "What is JavaScript?", "Compare them"],
    web_searches=[False, False, True]
)
```

#### Facebook Data

```python
# Scrape posts from profile
result = client.scrape.facebook.posts_by_profile(
    url="https://facebook.com/profile",
    num_of_posts=10,
    start_date="01-01-2025",
    end_date="12-31-2025",
    timeout=240
)

# Scrape posts from group
result = client.scrape.facebook.posts_by_group(
    url="https://facebook.com/groups/example",
    num_of_posts=20,
    timeout=240
)

# Scrape specific post
result = client.scrape.facebook.posts_by_url(
    url="https://facebook.com/post/123456",
    timeout=240
)

# Scrape comments from post
result = client.scrape.facebook.comments(
    url="https://facebook.com/post/123456",
    num_of_comments=100,
    start_date="01-01-2025",
    end_date="12-31-2025",
    timeout=240
)

# Scrape reels from profile
result = client.scrape.facebook.reels(
    url="https://facebook.com/profile",
    num_of_posts=50,
    timeout=240
)
```

#### Instagram Data

```python
# Scrape Instagram profile
result = client.scrape.instagram.profiles(
    url="https://instagram.com/username",
    timeout=240
)

# Scrape specific post
result = client.scrape.instagram.posts(
    url="https://instagram.com/p/ABC123",
    timeout=240
)

# Scrape comments from post
result = client.scrape.instagram.comments(
    url="https://instagram.com/p/ABC123",
    timeout=240
)

# Scrape specific reel
result = client.scrape.instagram.reels(
    url="https://instagram.com/reel/ABC123",
    timeout=240
)

# Discover posts from profile (with filters)
result = client.search.instagram.posts(
    url="https://instagram.com/username",
    num_of_posts=10,
    start_date="01-01-2025",
    end_date="12-31-2025",
    post_type="reel",
    timeout=240
)

# Discover reels from profile
result = client.search.instagram.reels(
    url="https://instagram.com/username",
    num_of_posts=50,
    start_date="01-01-2025",
    end_date="12-31-2025",
    timeout=240
)
```

### Search Engine Results (SERP)

```python
# Google search
result = client.search.google(
    query="python tutorial",
    location="United States",
    language="en",
    num_results=20
)

# Access results
for item in result.data:
    print(f"{item['position']}. {item['title']}")
    print(f"   {item['url']}")

# Bing search
result = client.search.bing(
    query="python tutorial",
    location="United States"
)

# Yandex search
result = client.search.yandex(
    query="python tutorial",
    location="Russia"
)
```

### Async Usage

For better performance with multiple operations, use async:

```python
import asyncio
from brightdata import BrightDataClient

async def scrape_multiple():
    # Use async context manager for engine lifecycle
    async with BrightDataClient() as client:
        # Scrape multiple URLs concurrently
        results = await client.scrape.generic.url_async([
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ])
        
        for result in results:
            print(f"Success: {result.success}")

asyncio.run(scrape_multiple())
```

**Important:** When using `*_async` methods, always use the async context manager (`async with BrightDataClient() as client`). Sync wrappers (methods without `_async`) handle this automatically.

---

## 🆕 What's New in v2 2.0.0

### 🆕 **Latest Updates (December 2025)**
- ✅ **Amazon Search API** - NEW parameter-based product discovery with correct dataset
- ✅ **LinkedIn Job Search Fixed** - Now builds URLs from keywords internally
- ✅ **Trigger Interface** - Manual trigger/poll/fetch control for all platforms
- ✅ **29 Sync Wrapper Fixes** - All sync methods work (scrapers + SERP API)
- ✅ **Batch Operations Fixed** - Returns List[ScrapeResult] correctly
- ✅ **Auto-Create Zones** - Now enabled by default (was opt-in)
- ✅ **Improved Zone Names** - `sdk_unlocker`, `sdk_serp`, `sdk_browser`
- ✅ **Full Sync/Async Examples** - README now shows both patterns for all features

### 🎓 **For Data Scientists**
- ✅ **5 Jupyter Notebooks** - Complete interactive tutorials
- ✅ **Pandas Integration** - Native DataFrame support with examples
- ✅ **Batch Processing Guide** - Scale to 1000s of URLs with progress bars
- ✅ **Cost Management** - Budget tracking and optimization
- ✅ **Visualization Examples** - matplotlib/seaborn integration

### 🎨 **Dataclass Payloads (Major Upgrade)**
- ✅ **Runtime Validation** - Catch errors at instantiation time
- ✅ **Helper Properties** - `.asin`, `.is_remote_search`, `.domain`, etc.
- ✅ **IDE Autocomplete** - Full IntelliSense support
- ✅ **Default Values** - Smart defaults (e.g., `country="US"`)
- ✅ **to_dict() Method** - Easy API conversion
- ✅ **Consistent Model** - Same pattern as result models

### 🖥️ **CLI Tool**
- ✅ **`brightdata` command** - Use SDK from terminal
- ✅ **Scrape operations** - `brightdata scrape amazon products ...`
- ✅ **Search operations** - `brightdata search amazon products --keyword ...`
- ✅ **Output formats** - JSON, pretty-print, minimal

### 🏗️ **Architecture Improvements**
- ✅ **Single AsyncEngine** - Shared across all scrapers (8x efficiency)
- ✅ **Resource Optimization** - Reduced memory footprint
- ✅ **Enhanced Error Messages** - Clear, actionable error messages
- ✅ **500+ Tests Passing** - Comprehensive test coverage (99.4%)

### 🆕 **Platforms & Features**
- ✅ **Amazon Search** - Keyword-based product discovery
- ✅ **Facebook Scraper** - Posts (profile/group/URL), Comments, Reels
- ✅ **Instagram Scraper** - Profiles, Posts, Comments, Reels
- ✅ **Instagram Search** - Posts and Reels discovery with filters

---

## 🏗️ Architecture

### Hierarchical Service Access

The SDK provides a clean, intuitive interface organized by operation type:

```python
client = BrightDataClient()

# URL-based extraction (scrape namespace)
client.scrape.amazon.products(url="...")
client.scrape.linkedin.profiles(url="...")
client.scrape.facebook.posts_by_profile(url="...")
client.scrape.instagram.profiles(url="...")
client.scrape.generic.url(url="...")

# Parameter-based discovery (search namespace)
client.search.amazon.products(keyword="...", min_price=..., max_price=...)
client.search.linkedin.jobs(keyword="...", location="...")
client.search.instagram.posts(url="...", num_of_posts=10)
client.search.google(query="...")
client.scrape.chatgpt.prompt(prompt="...")

# Direct service access (advanced)
client.web_unlocker.fetch(url="...")
client.crawler.discover(url="...")  # Coming soon
```

### Core Components

- **`BrightDataClient`** - Main entry point with authentication and .env support
- **`ScrapeService`** - URL-based data extraction
- **`SearchService`** - Parameter-based discovery
- **Result Models** - `ScrapeResult`, `SearchResult`, `CrawlResult` with method tracking
- **Platform Scrapers** - Amazon, LinkedIn, ChatGPT, Facebook, Instagram with registry pattern
- **SERP Services** - Google, Bing, Yandex search
- **Type System** - 100% type safety with TypedDict
- **Constants Module** - Centralized configuration (no magic numbers)
- **SSL Helpers** - Platform-specific error guidance
- **Function Detection** - Automatic SDK function tracking for monitoring

---

## 📚 API Reference

### Client Initialization

```python
client = BrightDataClient(
    token="your_token",               # Auto-loads from BRIGHTDATA_API_TOKEN if not provided
    customer_id="your_customer_id",   # Auto-loads from BRIGHTDATA_CUSTOMER_ID (optional)
    timeout=30,                        # Default timeout in seconds
    web_unlocker_zone="sdk_unlocker",  # Web Unlocker zone name (default)
    serp_zone="sdk_serp",              # SERP API zone name (default)
    browser_zone="sdk_browser",        # Browser API zone name (default)
    auto_create_zones=True,            # Auto-create missing zones (default: True)
    validate_token=False               # Validate token on init (default: False)
)
```

**Environment Variables:**
- `BRIGHTDATA_API_TOKEN` - Your API token (required)
- `BRIGHTDATA_CUSTOMER_ID` - Your customer ID (optional)

Both are automatically loaded from environment or `.env` file.

### Connection Testing

```python
# Test API connection
is_valid = await client.test_connection()
is_valid = client.test_connection_sync()  # Synchronous version

# Get account information
info = await client.get_account_info()
info = client.get_account_info_sync()

print(f"Zones: {info['zone_count']}")
print(f"Active zones: {[z['name'] for z in info['zones']]}")
```

### Zone Management

The SDK can automatically create required zones if they don't exist, or you can manage zones manually.

#### Automatic Zone Creation

Enable automatic zone creation when initializing the client:

```python
client = BrightDataClient(
    token="your_token",
    auto_create_zones=True  # Automatically create zones if missing
)

# Zones are created on first API call
async with client:
    # sdk_unlocker, sdk_serp, and sdk_browser zones created automatically if needed
    result = await client.scrape.amazon.products(url="...")
```

#### Manual Zone Management

List and manage zones programmatically:

```python
# List all zones
zones = await client.list_zones()
zones = client.list_zones_sync()  # Synchronous version

for zone in zones:
    print(f"Zone: {zone['name']} (Type: {zone.get('type', 'unknown')})")

# Advanced: Use ZoneManager directly
from brightdata import ZoneManager

async with client.engine:
    zone_manager = ZoneManager(client.engine)

    # Ensure specific zones exist
    await zone_manager.ensure_required_zones(
        web_unlocker_zone="my_custom_zone",
        serp_zone="my_serp_zone"
    )
```

**Zone Creation API:**
- Endpoint: `POST https://api.brightdata.com/zone`
- Zones are created via the Bright Data API
- Supported zone types: `unblocker`, `serp`, `browser`
- Automatically handles duplicate zones gracefully

### Result Objects

All operations return rich result objects with timing and metadata:

```python
result = client.scrape.amazon.products(url="...")

# Access data
result.success       # bool - Operation succeeded
result.data          # Any - Scraped data
result.error         # str | None - Error message if failed
result.cost          # float | None - Cost in USD
result.platform      # str | None - Platform name (e.g., "linkedin", "amazon")
result.method        # str | None - Method used: "web_scraper", "web_unlocker", "browser_api"

# Timing information
result.elapsed_ms()              # Total time in milliseconds
result.get_timing_breakdown()    # Detailed timing dict

# Serialization
result.to_dict()                 # Convert to dictionary
result.to_json(indent=2)         # JSON string
result.save_to_file("result.json")  # Save to file
```

---

## 🖥️ CLI Usage

The SDK includes a powerful CLI tool:

```bash
# Help
brightdata --help

# Scrape Amazon product (URL is positional argument)
brightdata scrape amazon products \
  "https://amazon.com/dp/B0CRMZHDG8"

# Search LinkedIn jobs
brightdata search linkedin jobs \
  --keyword "python developer" \
  --location "New York" \
  --remote \
  --output-file jobs.json

# Search Google (query is positional argument)
brightdata search google \
  "python tutorial" \
  --location "United States"

# Generic web scraping (URL is positional argument)
brightdata scrape generic \
  "https://example.com" \
  --response-format raw \
  --output-format pretty
```

### Available Commands

**Scrape Operations:**
- `brightdata scrape amazon products/reviews/sellers`
- `brightdata scrape linkedin profiles/jobs/companies/posts`
- `brightdata scrape facebook posts-profile/posts-group/comments/reels`
- `brightdata scrape instagram profiles/posts/comments/reels`
- `brightdata scrape chatgpt prompt`
- `brightdata scrape generic url`

**Search Operations:**
- `brightdata search amazon products`
- `brightdata search linkedin jobs/profiles/posts`
- `brightdata search instagram posts/reels`
- `brightdata search google/bing/yandex`
- `brightdata search chatgpt`

### CLI Output Formats

The CLI supports two different format parameters for different purposes:

#### Global Output Format (`--output-format`)

Controls **how results are displayed** (available for ALL commands):

```bash
# JSON format (default) - Full structured output
brightdata scrape amazon products "https://amazon.com/dp/B123" --output-format json

# Pretty format - Human-readable with formatted output
brightdata scrape amazon products "https://amazon.com/dp/B123" --output-format pretty

# Minimal format - Just the data, no metadata
brightdata scrape amazon products "https://amazon.com/dp/B123" --output-format minimal
```

#### Generic Scraper Response Format (`--response-format`)

Controls **what the API returns** (generic scraper only):

```bash
# Raw format (default) - Returns HTML/text as-is
brightdata scrape generic "https://example.com" --response-format raw

# JSON format - API attempts to parse as JSON
brightdata scrape generic "https://api.example.com/data" --response-format json
```

**Note:** You can combine both:
```bash
brightdata scrape generic "https://example.com" \
  --response-format raw \
  --output-format pretty
```

---

## 🐼 Pandas Integration

Perfect for data analysis workflows:

```python
import pandas as pd
from tqdm import tqdm
from brightdata import BrightDataClient
from brightdata.payloads import AmazonProductPayload

client = BrightDataClient()

# Batch scrape with progress bar
urls = ["https://amazon.com/dp/B001", "https://amazon.com/dp/B002"]
results = []

for url in tqdm(urls, desc="Scraping"):
    payload = AmazonProductPayload(url=url)
    result = client.scrape.amazon.products(**payload.to_dict())
    
    if result.success:
        results.append({
            'asin': payload.asin,
            'title': result.data.get('title'),
            'price': result.data.get('final_price'),
            'rating': result.data.get('rating'),
            'cost': result.cost,
            'elapsed_ms': result.elapsed_ms()
        })

# Create DataFrame
df = pd.DataFrame(results)

# Analysis
print(df.describe())
print(f"Total cost: ${df['cost'].sum():.4f}")
print(f"Avg rating: {df['rating'].mean():.2f}")

# Export
df.to_csv('amazon_products.csv', index=False)
df.to_excel('amazon_products.xlsx', index=False)

# Visualization
import matplotlib.pyplot as plt
df.plot(x='asin', y='rating', kind='bar', title='Product Ratings')
plt.show()
```

See **[notebooks/02_pandas_integration.ipynb](notebooks/02_pandas_integration.ipynb)** for complete examples.

---

## 🎨 Dataclass Payloads

All payloads are now dataclasses with runtime validation:

### Amazon Payloads

```python
from brightdata.payloads import AmazonProductPayload, AmazonReviewPayload

# Product with validation
payload = AmazonProductPayload(
    url="https://amazon.com/dp/B123456789",
    reviews_count=50,
    images_count=10
)

# Helper properties
print(payload.asin)        # "B123456789"
print(payload.domain)      # "amazon.com"
print(payload.is_secure)   # True

# Convert to API dict
api_dict = payload.to_dict()  # Excludes None values
```

### LinkedIn Payloads

```python
from brightdata.payloads import LinkedInJobSearchPayload

payload = LinkedInJobSearchPayload(
    keyword="python developer",
    location="San Francisco",
    remote=True,
    experienceLevel="mid"
)

# Helper properties
print(payload.is_remote_search)  # True

# Use with client
result = client.search.linkedin.jobs(**payload.to_dict())
```

### ChatGPT Payloads

```python
from brightdata.payloads import ChatGPTPromptPayload

payload = ChatGPTPromptPayload(
    prompt="Explain async programming",
    web_search=True
)

# Default values
print(payload.country)  # "US" (default)
print(payload.uses_web_search)  # True
```

### Validation Examples

```python
# Runtime validation catches errors early
try:
    AmazonProductPayload(url="invalid-url")
except ValueError as e:
    print(e)  # "url must be valid HTTP/HTTPS URL"

try:
    AmazonProductPayload(
        url="https://amazon.com/dp/B123",
        reviews_count=-1
    )
except ValueError as e:
    print(e)  # "reviews_count must be non-negative"
```

---

## 🔧 Advanced Usage

### Batch Operations

```python
# Scrape multiple URLs concurrently
urls = [
    "https://amazon.com/dp/B001",
    "https://amazon.com/dp/B002",
    "https://amazon.com/dp/B003"
]

results = client.scrape.amazon.products(url=urls)

for result in results:
    if result.success:
        print(f"{result.data['title']}: ${result.data['price']}")
```

### Platform-Specific Options

```python
# Amazon reviews with filters
result = client.scrape.amazon.reviews(
    url="https://amazon.com/dp/B123",
    pastDays=7,              # Last 7 days only
    keyWord="quality",       # Filter by keyword
    numOfReviews=50          # Limit to 50 reviews
)

# LinkedIn jobs with extensive filters
result = client.search.linkedin.jobs(
    keyword="python developer",
    location="New York",
    country="us",
    jobType="full-time",
    experienceLevel="mid",
    remote=True,
    company="Microsoft",
    timeRange="past-week"
)
```

### Sync vs Async Examples - Full Coverage

All SDK methods support **both sync and async** patterns. Choose based on your needs:

#### **Amazon Products**

```python
# SYNC - Simple scripts
result = client.scrape.amazon.products(url="https://amazon.com/dp/B123")

# ASYNC - Concurrent operations
import asyncio

async def scrape_amazon():
    async with BrightDataClient() as client:
        result = await client.scrape.amazon.products_async(url="https://amazon.com/dp/B123")
        return result

result = asyncio.run(scrape_amazon())
```

#### **Amazon Search**

```python
# SYNC - Simple keyword search
result = client.search.amazon.products(keyword="laptop", prime_eligible=True)

# ASYNC - Batch keyword searches
async def search_amazon():
    async with BrightDataClient() as client:
        result = await client.search.amazon.products_async(
            keyword="laptop",
            min_price=50000,
            max_price=200000,
            prime_eligible=True
        )
        return result

result = asyncio.run(search_amazon())
```

#### **LinkedIn Scraping**

```python
# SYNC - Single profile
result = client.scrape.linkedin.profiles(url="https://linkedin.com/in/johndoe")

# ASYNC - Multiple profiles concurrently
async def scrape_linkedin():
    async with BrightDataClient() as client:
        urls = ["https://linkedin.com/in/person1", "https://linkedin.com/in/person2"]
        results = await client.scrape.linkedin.profiles_async(url=urls)
        return results

results = asyncio.run(scrape_linkedin())
```

#### **LinkedIn Job Search**

```python
# SYNC - Simple job search
result = client.search.linkedin.jobs(keyword="python", location="NYC", remote=True)

# ASYNC - Advanced search with filters
async def search_jobs():
    async with BrightDataClient() as client:
        result = await client.search.linkedin.jobs_async(
            keyword="python developer",
            location="New York",
            experienceLevel="mid",
            jobType="full-time",
            remote=True
        )
        return result

result = asyncio.run(search_jobs())
```

#### **SERP API (Google, Bing, Yandex)**

```python
# SYNC - Quick Google search
result = client.search.google(query="python tutorial", location="United States")

# ASYNC - Multiple search engines concurrently
async def search_all_engines():
    async with BrightDataClient() as client:
        google = await client.search.google_async(query="python", num_results=10)
        bing = await client.search.bing_async(query="python", num_results=10)
        yandex = await client.search.yandex_async(query="python", num_results=10)
        return google, bing, yandex

results = asyncio.run(search_all_engines())
```

#### **Facebook Scraping**

```python
# SYNC - Single profile posts
result = client.scrape.facebook.posts_by_profile(
    url="https://facebook.com/profile",
    num_of_posts=10
)

# ASYNC - Multiple sources
async def scrape_facebook():
    async with BrightDataClient() as client:
        profile_posts = await client.scrape.facebook.posts_by_profile_async(
            url="https://facebook.com/zuck",
            num_of_posts=10
        )
        group_posts = await client.scrape.facebook.posts_by_group_async(
            url="https://facebook.com/groups/programming",
            num_of_posts=10
        )
        return profile_posts, group_posts

results = asyncio.run(scrape_facebook())
```

#### **Instagram Scraping**

```python
# SYNC - Single profile
result = client.scrape.instagram.profiles(url="https://instagram.com/instagram")

# ASYNC - Profile + posts
async def scrape_instagram():
    async with BrightDataClient() as client:
        profile = await client.scrape.instagram.profiles_async(
            url="https://instagram.com/instagram"
        )
        posts = await client.scrape.instagram.posts_async(
            url="https://instagram.com/p/ABC123"
        )
        return profile, posts

results = asyncio.run(scrape_instagram())
```

#### **ChatGPT**

```python
# SYNC - Single prompt
result = client.scrape.chatgpt.prompt(prompt="Explain Python", web_search=True)

# ASYNC - Batch prompts
async def ask_chatgpt():
    async with BrightDataClient() as client:
        result = await client.scrape.chatgpt.prompts_async(
            prompts=["What is Python?", "What is JavaScript?"],
            web_searches=[False, True]
        )
        return result

result = asyncio.run(ask_chatgpt())
```

#### **Generic Web Scraping**

```python
# SYNC - Single URL
result = client.scrape.generic.url(url="https://example.com")

# ASYNC - Concurrent scraping
async def scrape_multiple():
    async with BrightDataClient() as client:
        results = await client.scrape.generic.url_async([
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ])
        return results

results = asyncio.run(scrape_multiple())
```

---

### **When to Use Sync vs Async**

**Use Sync When:**
- ✅ Simple scripts or notebooks
- ✅ Single operations at a time
- ✅ Learning or prototyping
- ✅ Sequential workflows

**Use Async When:**
- ✅ Scraping multiple URLs concurrently
- ✅ Combining multiple API calls
- ✅ Production applications
- ✅ Performance-critical operations

**Note:** Sync wrappers (e.g., `profiles()`) internally use `asyncio.run()` and cannot be called from within an existing async context. Use `*_async` methods when you're already in an async function.

### SSL Certificate Error Handling

The SDK includes comprehensive SSL error handling with platform-specific guidance:

```python
from brightdata import BrightDataClient
from brightdata.exceptions import SSLError

try:
    client = BrightDataClient()
    result = client.scrape.generic.url("https://example.com")
except SSLError as e:
    # Helpful error message with platform-specific fix instructions
    print(e)
    # On macOS, suggests:
    # - pip install --upgrade certifi
    # - Running Install Certificates.command
    # - Setting SSL_CERT_FILE environment variable
```

**Common SSL fixes:**

```bash
# Option 1: Upgrade certifi
pip install --upgrade certifi

# Option 2: Set SSL_CERT_FILE (macOS/Linux)
export SSL_CERT_FILE=$(python -m certifi)

# Option 3: Run Install Certificates (macOS python.org installers)
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Code Quality Improvements (PR #6)

Recent architectural refactoring includes:

#### 1. **Centralized Constants Module**
All magic numbers moved to `constants.py`:
```python
from brightdata.constants import (
    DEFAULT_POLL_INTERVAL,      # 10 seconds
    DEFAULT_POLL_TIMEOUT,       # 600 seconds
    DEFAULT_TIMEOUT_SHORT,      # 180 seconds
    DEFAULT_TIMEOUT_MEDIUM,     # 240 seconds
    DEFAULT_COST_PER_RECORD,    # 0.001 USD
)
```

#### 2. **Method Field Instead of Fallback**
Results now track which method was used:
```python
result = client.scrape.amazon.products(url="...")
print(result.method)  # "web_scraper", "web_unlocker", or "browser_api"
```

#### 3. **Function-Level Monitoring**
Automatic tracking of which SDK functions are called:
```python
# Automatically detected and sent in API requests
result = client.scrape.linkedin.profiles(url="...")
# Internal: sdk_function="profiles" sent to Bright Data
```

#### 4. **Service Class Separation**
Clean separation of concerns:
- `ScrapeService` - URL-based extraction
- `SearchService` - Parameter-based discovery  
- `CrawlerService` - Web crawling (coming soon)
- `WebUnlockerService` - Direct proxy access

#### 5. **Enhanced SSL Error Handling**
Platform-specific guidance for certificate issues:
```python
from brightdata.utils.ssl_helpers import (
    is_ssl_certificate_error,
    get_ssl_error_message
)
```

---

## 🧪 Testing

The SDK includes 365+ comprehensive tests:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/e2e/               # End-to-end tests

# Run with coverage
pytest tests/ --cov=brightdata --cov-report=html
```

---

## 🏛️ Design Philosophy

- **Client is single source of truth** for configuration
- **Authentication "just works"** with minimal setup
- **Fail fast and clearly** when credentials are missing/invalid
- **Each platform is an expert** in its domain
- **Scrape vs Search distinction** is clear and consistent
- **Build for future** - registry pattern enables intelligent routing

---

## 📖 Documentation

### Jupyter Notebooks (Interactive)
- [01_quickstart.ipynb](notebooks/01_quickstart.ipynb) - 5-minute getting started
- [02_pandas_integration.ipynb](notebooks/02_pandas_integration.ipynb) - DataFrame workflows
- [03_amazon_scraping.ipynb](notebooks/03_amazon_scraping.ipynb) - Amazon deep dive
- [04_linkedin_jobs.ipynb](notebooks/04_linkedin_jobs.ipynb) - Job market analysis
- [05_batch_processing.ipynb](notebooks/05_batch_processing.ipynb) - Scale to production

### Code Examples
- [examples/10_pandas_integration.py](examples/10_pandas_integration.py) - Pandas integration
- [examples/01_simple_scrape.py](examples/01_simple_scrape.py) - Basic usage
- [examples/03_batch_scraping.py](examples/03_batch_scraping.py) - Batch operations
- [examples/04_specialized_scrapers.py](examples/04_specialized_scrapers.py) - Platform-specific
- [All examples →](examples/)

### Documentation
- [API Reference](docs/api-reference/)
- [Contributing Guidelines](https://github.com/brightdata/sdk-python/blob/main/CONTRIBUTING.md) (See upstream repo)

---

## 🔧 Troubleshooting

### SSL Certificate Errors (macOS)

If you encounter SSL certificate verification errors, especially on macOS:

```
SSL: CERTIFICATE_VERIFY_FAILED
```

The SDK will provide helpful, platform-specific guidance. Quick fixes:

```bash
# Option 1: Upgrade certifi
pip install --upgrade certifi

# Option 2: Set SSL_CERT_FILE environment variable
export SSL_CERT_FILE=$(python -m certifi)

# Option 3: Run Install Certificates (macOS with python.org installer)
/Applications/Python\ 3.x/Install\ Certificates.command

# Option 4: Install via Homebrew (if using Homebrew Python)
brew install ca-certificates
```

### Missing Token

```python
# Error: BRIGHTDATA_API_TOKEN not found in environment

# Solution 1: Create .env file
echo "BRIGHTDATA_API_TOKEN=your_token" > .env

# Solution 2: Export environment variable
export BRIGHTDATA_API_TOKEN="your_token"

# Solution 3: Pass directly to client
client = BrightDataClient(token="your_token")
```

### Import Errors

```bash
# If you get import errors, ensure package is installed
pip install --upgrade brightdata-sdk

# For development installation
pip install -e .
```

---

## 🤝 Contributing

Contributions are welcome! Check the [GitHub repository](https://github.com/brightdata/sdk-python) for contribution guidelines.

### Development Setup

```bash
git clone https://github.com/brightdata/sdk-python.git
cd sdk-python

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

---

## 📊 Project Stats

- **Production Code:** ~9,000 lines
- **Test Code:** ~4,000 lines
- **Documentation:** 5 Jupyter notebooks + 10 examples
- **Test Coverage:** 502+ tests passing (Unit, Integration, E2E)
- **Supported Platforms:** Amazon, LinkedIn, ChatGPT, Facebook, Instagram, Generic Web
- **Supported Search Engines:** Google, Bing, Yandex
- **Type Safety:** 100% (Dataclasses + TypedDict)
- **Resource Efficiency:** Single shared AsyncEngine
- **Data Science Ready:** Pandas, tqdm, joblib integration
- **CLI Tool:** Full-featured command-line interface
- **Code Quality:** Enterprise-grade, FAANG standards

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [Bright Data](https://brightdata.com) - Get your API token
- [API Documentation](https://docs.brightdata.com)
- [GitHub Repository](https://github.com/brightdata/sdk-python)
- [Issue Tracker](https://github.com/brightdata/sdk-python/issues)

---

## 💡 Examples

### Complete Workflow Example

```python
from brightdata import BrightDataClient

# Initialize (auto-loads from .env or environment)
client = BrightDataClient()

# Test connection
if client.test_connection_sync():
    print("✅ Connected to Bright Data API")
    
    # Get account info
    info = client.get_account_info_sync()
    print(f"Active zones: {info['zone_count']}")
    
    # Scrape Amazon product
    product = client.scrape.amazon.products(
        url="https://amazon.com/dp/B0CRMZHDG8"
    )
    
    if product.success:
        print(f"Product: {product.data[0]['title']}")
        print(f"Price: {product.data[0]['final_price']}")
        print(f"Rating: {product.data[0]['rating']}")
        print(f"Cost: ${product.cost:.4f}")
    
    # Search LinkedIn jobs
    jobs = client.search.linkedin.jobs(
        keyword="python developer",
        location="San Francisco",
        remote=True
    )
    
    if jobs.success:
        print(f"Found {len(jobs.data)} jobs")
    
    # Scrape Facebook posts
    fb_posts = client.scrape.facebook.posts_by_profile(
        url="https://facebook.com/zuck",
        num_of_posts=10,
        timeout=240
    )
    
    if fb_posts.success:
    print(f"Scraped {len(fb_posts.data)} Facebook posts")
    
    # Scrape Instagram profile
    ig_profile = client.scrape.instagram.profiles(
        url="https://instagram.com/instagram",
        timeout=240
    )
    
    if ig_profile.success:
        print(f"Profile: {ig_profile.data[0]['username']}")
        print(f"Followers: {ig_profile.data[0]['followers_count']}")
    
    # Search Google
    search_results = client.search.google(
        query="python async tutorial",
        location="United States",
        num_results=10
    )
    
    if search_results.success:
        for i, item in enumerate(search_results.data[:5], 1):
            print(f"{i}. {item.get('title', 'N/A')}")
```

### Interactive CLI Demo

Run the included demo to explore the SDK interactively:

```bash
python demo_sdk.py
```
---

## 🙏 Acknowledgments

Built with best practices from:
- Modern Python packaging (PEP 518, 621)
- Async/await patterns
- Type safety (PEP 484, 544, dataclasses)
- Enterprise-grade engineering standards
- Data science workflows (pandas, jupyter)

### Built For
- 🎓 **Data Scientists** - Jupyter notebooks, pandas integration, visualization examples
- 👨‍💻 **Developers** - Type-safe API, comprehensive docs, CLI tool
- 🏢 **Enterprises** - Production-ready, well-tested, resource-efficient

---

## 🌟 Why Choose This SDK?

- ✅ **Data Scientist Friendly** - 5 Jupyter notebooks, pandas examples, visualization guides
- ✅ **Type Safe** - Dataclass payloads with runtime validation
- ✅ **Enterprise Ready** - 502+ tests, resource efficient, production-proven
- ✅ **Well Documented** - Interactive notebooks + code examples + API docs
- ✅ **Easy to Use** - CLI tool, intuitive API, helpful error messages
- ✅ **Actively Maintained** - Regular updates, bug fixes, new features

---

**Ready to start scraping?** Get your API token at [brightdata.com](https://brightdata.com/cp/api_keys) and try our [quickstart notebook](notebooks/01_quickstart.ipynb)!

