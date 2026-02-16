# Bright Data CLI

Command-line interface for Bright Data Python SDK.

## Installation

The CLI is automatically installed with the SDK:

```bash
pip install brightdata-sdk
```

## Usage

### Authentication

All commands require an API key. You can provide it in three ways:

1. **Command-line flag** (highest priority):
   ```bash
   brightdata scrape amazon products --api-key YOUR_API_KEY https://amazon.com/dp/...
   ```

2. **Environment variable**:
   ```bash
   export BRIGHTDATA_API_TOKEN=YOUR_API_KEY
   brightdata scrape amazon products https://amazon.com/dp/...
   ```

3. **Interactive prompt** (if neither is provided):
   ```bash
   brightdata scrape amazon products https://amazon.com/dp/...
   # Will prompt: Enter your Bright Data API key:
   ```

### Scrape Commands (URL-based extraction)

#### Generic Scraper
```bash
brightdata scrape generic <URL> [--country CODE] [--response-format FORMAT]
```

#### Amazon
```bash
# Products
brightdata scrape amazon products <URL> [--timeout SECONDS]

# Reviews
brightdata scrape amazon reviews <URL> [--past-days DAYS] [--keyword KEYWORD] [--num-reviews NUM] [--timeout SECONDS]

# Sellers
brightdata scrape amazon sellers <URL> [--timeout SECONDS]
```

#### LinkedIn
```bash
# Profiles
brightdata scrape linkedin profiles <URL> [--timeout SECONDS]

# Posts
brightdata scrape linkedin posts <URL> [--timeout SECONDS]

# Jobs
brightdata scrape linkedin jobs <URL> [--timeout SECONDS]

# Companies
brightdata scrape linkedin companies <URL> [--timeout SECONDS]
```

#### Facebook
```bash
# Posts by profile
brightdata scrape facebook posts-by-profile <URL> [--num-posts NUM] [--start-date DATE] [--end-date DATE] [--timeout SECONDS]

# Posts by group
brightdata scrape facebook posts-by-group <URL> [--num-posts NUM] [--start-date DATE] [--end-date DATE] [--timeout SECONDS]

# Posts by URL
brightdata scrape facebook posts-by-url <URL> [--timeout SECONDS]

# Comments
brightdata scrape facebook comments <URL> [--num-comments NUM] [--start-date DATE] [--end-date DATE] [--timeout SECONDS]

# Reels
brightdata scrape facebook reels <URL> [--num-posts NUM] [--start-date DATE] [--end-date DATE] [--timeout SECONDS]
```

#### Instagram
```bash
# Profiles
brightdata scrape instagram profiles <URL> [--timeout SECONDS]

# Posts
brightdata scrape instagram posts <URL> [--timeout SECONDS]

# Comments
brightdata scrape instagram comments <URL> [--timeout SECONDS]

# Reels
brightdata scrape instagram reels <URL> [--timeout SECONDS]
```

#### ChatGPT
```bash
brightdata scrape chatgpt prompt <PROMPT> [--country CODE] [--web-search] [--additional-prompt PROMPT] [--timeout SECONDS]
```

### Search Commands (Parameter-based discovery)

#### SERP Services
```bash
# Google
brightdata search google <QUERY> [--location LOCATION] [--language CODE] [--device TYPE] [--num-results NUM]

# Bing
brightdata search bing <QUERY> [--location LOCATION] [--language CODE] [--num-results NUM]

# Yandex
brightdata search yandex <QUERY> [--location LOCATION] [--language CODE] [--num-results NUM]
```

#### LinkedIn Search
```bash
# Posts
brightdata search linkedin posts <PROFILE_URL> [--start-date DATE] [--end-date DATE] [--timeout SECONDS]

# Profiles
brightdata search linkedin profiles <FIRST_NAME> [--last-name LAST_NAME] [--timeout SECONDS]

# Jobs
brightdata search linkedin jobs [--url URL] [--keyword KEYWORD] [--location LOCATION] [--country CODE] [--remote] [--timeout SECONDS]
```

#### ChatGPT Search
```bash
brightdata search chatgpt prompt <PROMPT> [--country CODE] [--web-search] [--secondary-prompt PROMPT] [--timeout SECONDS]
```

#### Instagram Search
```bash
# Posts
brightdata search instagram posts <URL> [--num-posts NUM] [--start-date DATE] [--end-date DATE] [--post-type TYPE] [--timeout SECONDS]

# Reels
brightdata search instagram reels <URL> [--num-posts NUM] [--start-date DATE] [--end-date DATE] [--timeout SECONDS]
```

### Output Options

All commands support output formatting:

```bash
# JSON format (default)
brightdata scrape amazon products <URL> --output-format json

# Pretty format (human-readable)
brightdata scrape amazon products <URL> --output-format pretty

# Minimal format (just the data)
brightdata scrape amazon products <URL> --output-format minimal

# Save to file
brightdata scrape amazon products <URL> --output-file results.json
```

### Examples

```bash
# Scrape Amazon product
brightdata scrape amazon products https://amazon.com/dp/B0123456 --api-key YOUR_KEY

# Search Google
brightdata search google "python tutorial" --location "United States" --num-results 20

# Scrape LinkedIn profile
brightdata scrape linkedin profiles https://linkedin.com/in/johndoe

# Search LinkedIn jobs
brightdata search linkedin jobs --keyword "python developer" --location "New York" --remote

# Scrape Instagram profile
brightdata scrape instagram profiles https://instagram.com/username

# Send ChatGPT prompt
brightdata scrape chatgpt prompt "Explain async programming" --web-search --country us
```

## Help

Get help for any command:

```bash
brightdata --help
brightdata scrape --help
brightdata scrape amazon --help
brightdata search --help
```
