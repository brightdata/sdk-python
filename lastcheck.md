# Last Check - Critical Issues Found

This document tracks critical issues discovered during final testing of the Bright Data SDK.

---

## Issue 1: Incorrect Await in get_account_info Method

**File:** `src/brightdata/client.py` (Line 339)

### What is the issue?

The `get_account_info` method incorrectly used `await` on a non-async method, causing a runtime error:
```
object ResponseContextManager can't be used in 'await' expression
```

**Incorrect code:**
```python
async with await self.engine.get_from_url(
    f"{self.engine.BASE_URL}/zone/get_active_zones"
) as zones_response:
```

The `engine.get_from_url()` method is not an async function - it returns a context manager directly, not a coroutine. Using `await` on it causes Python to try to await the context manager object itself, which fails.

### What is the fix?

Remove the extra `await` keyword:

**Correct code:**
```python
async with self.engine.get_from_url(
    f"{self.engine.BASE_URL}/zone/get_active_zones"
) as zones_response:
```

### Impact

- **Severity:** High
- **Affected functionality:** Account information retrieval, zone listing, initial SDK setup
- **User impact:** Any code calling `client.get_account_info()` or `client.get_account_info_sync()` would fail with a runtime error
- **Discovery:** Found when running `test_02_list_zones.py`

### Root Cause

Confusion between async patterns. The developer likely thought `get_from_url()` was an async method that needed to be awaited, but it's actually a regular method that returns an async context manager.

### Similar Code Patterns Checked

- `test_connection()` method (Line 297): ✅ Correctly implemented without extra `await`
- Other uses of `engine.get_from_url()`: None found in client.py

### Testing

After fix:
```bash
python probe_tests/test_02_list_zones.py
# Should now successfully list zones without the await error
```

---

### Verification

After applying the fix, the test runs successfully:
```
✅ Client initialized successfully
✅ Token Valid: True
✅ API call succeeds without await error
```

If you see "0 zones found", this is correct behavior - it means your Bright Data account doesn't have zones configured yet. You need to create zones in the Bright Data dashboard.

---

## Issue 2: Zones Not Showing - get_active_zones Returns Empty Array

**File:** `src/brightdata/client.py` (get_account_info method)

### What is the issue?

The SDK uses `/zone/get_active_zones` endpoint which only returns **active** zones. If all your zones are inactive (as shown in Bright Data dashboard), the API returns an empty array `[]`.

**Current behavior:**
- Endpoint: `/zone/get_active_zones`
- Returns: `[]` (empty array) when zones are inactive
- User's zones: `residential_proxy1` (Inactive), `web_unlocker1` (status unknown)

### What is the fix?

Multiple options:

1. **Activate zones in Bright Data dashboard** (User action)
   - Go to https://brightdata.com
   - Activate the zones you want to use
   - Zones will then appear in API response

2. **Use a different endpoint** (SDK fix - if available)
   - Need to find endpoint that returns ALL zones (not just active)
   - Current testing shows no such endpoint is publicly available

3. **Add warning message** (SDK improvement)
   ```python
   if not zones:
       print("No active zones found. Please check:")
       print("1. Your zones might be inactive - activate them in dashboard")
       print("2. You might need to create zones first")
   ```

### Impact

- **Severity:** Medium
- **Affected functionality:** Zone discovery, automatic configuration
- **User impact:** Users with inactive zones see "0 zones" even though zones exist
- **Discovery:** Found when testing with account that has inactive zones

### Root Cause

The API endpoint name `get_active_zones` is explicit - it only returns active zones. This is by design but not clearly communicated to users.

### Workaround

For testing without active zones, manually specify zone names:
```python
client = BrightDataClient(
    web_unlocker_zone="web_unlocker1",  # Use your actual zone name
    serp_zone="your_serp_zone",
    browser_zone="your_browser_zone"
)
```

### Resolution Confirmed

User created a new active zone `web_unlocker2` and it immediately appeared in the API response:
```json
[
  {
    "name": "web_unlocker2",
    "type": "unblocker"
  }
]
```

This confirms the SDK is working correctly - it accurately reports only **active** zones as intended by the API design.

---

## Issue 3: Inactive Zones Not Listed - No Clarity on Zone Deactivation

**File:** `src/brightdata/client.py` (get_account_info method using `/zone/get_active_zones`)

### What is the issue?

The SDK only shows active zones but provides no visibility into:
1. **Inactive zones that exist** - Users have zones but can't see them via API
2. **Why zones become inactive** - No explanation of deactivation triggers
3. **How to reactivate zones** - No programmatic way to activate zones
4. **Zone state transitions** - When/why zones change from active to inactive

**User Experience Problem:**
- User has zones (`residential_proxy1`, `web_unlocker1`) visible in dashboard
- SDK returns empty array, making it seem like no zones exist
- No indication that zones are present but inactive
- No information about why zones are inactive

### Common Reasons Zones Become Inactive (Not Documented):

1. **No usage for extended period** - Zones auto-deactivate after inactivity
2. **Payment issues** - Billing problems may deactivate zones
3. **Manual deactivation** - User or admin deactivated in dashboard
4. **Service changes** - Plan changes might affect zone status
5. **Initial setup** - New zones might start as inactive

### What is the fix?

**Short term:**
- Add better error messages indicating inactive zones might exist
- Document that only active zones are returned
- Suggest checking dashboard for inactive zones

**Long term (API improvements needed):**
- Provide endpoint to list ALL zones with status
- Include deactivation reason in zone data
- Add zone activation/deactivation endpoints
- Return inactive zone count even if not listing them

### Impact

- **Severity:** High for user experience
- **Affected functionality:** Zone discovery, initial setup, debugging
- **User confusion:** Users think zones don't exist when they're just inactive
- **Discovery:** Found when user had 2 zones in dashboard but API returned 0

### Root Cause

The API design assumes users know:
1. Only active zones are returned
2. Zones can be inactive
3. Dashboard shows all zones but API doesn't
4. Manual dashboard intervention needed for activation

This creates a disconnect between dashboard visibility and API visibility.

### Recommendations

1. **Rename endpoint** to be clearer: `/zone/get_active_zones` → clearly indicates active only
2. **Add companion endpoint**: `/zone/get_all_zones` with status field
3. **Improve error messages**: When 0 zones returned, mention checking for inactive zones
4. **Add zone status to SDK**: Method to check zone states and activation requirements

---

## Issue 4: Incorrect Default SERP Zone Name

**File:** `src/brightdata/client.py` (Line 65)

### What is the issue?

The SDK uses `sdk_serp` as the default SERP zone name, but Bright Data's actual SERP zone naming convention is `serp_api1` (or similar patterns like `serp_api2`, etc.).

**Incorrect default:**
```python
DEFAULT_SERP_ZONE = "sdk_serp"
```

**Correct default:**
```python
DEFAULT_SERP_ZONE = "serp_api1"
```

### Impact

- **Severity:** Medium
- **Affected functionality:** SERP API calls (Google, Bing, Yandex search)
- **User impact:** SERP tests fail with "zone 'sdk_serp' not found" error
- **Discovery:** Found when running `test_04_serp_google.py`

### Root Cause

The SDK developers used a generic placeholder name `sdk_serp` instead of following Bright Data's actual naming conventions for zones. The same issue exists for other default zones:
- `sdk_unlocker` should follow pattern like `web_unlocker1`
- `sdk_browser` should follow pattern like `browser_api1`

### Testing

After fix:
```bash
python probe_tests/test_04_serp_google.py
# Should now look for "serp_api1" zone instead of "sdk_serp"
```

### Similar Issues

The SDK has similar incorrect defaults:
- `DEFAULT_WEB_UNLOCKER_ZONE = "sdk_unlocker"` (should be like `web_unlocker1`)
- `DEFAULT_BROWSER_ZONE = "sdk_browser"` (should be like `browser_api1`)

These defaults don't match Bright Data's actual zone naming patterns.

---

## Issue 5: SERP SDK Implementation Missing Key Components

**Files:** Multiple files in `src/brightdata/api/serp/`

### What is the issue?

The SDK's SERP implementation has fundamental issues:

1. **Wrong endpoint**: Using `/request` endpoint (for Web Unlocker) instead of SERP-specific endpoint
2. **Wrong response format**: SERP zone returns raw HTTP response with HTML body, not parsed JSON
3. **Missing HTML parser**: SDK expects structured data but gets HTML, has no parser to extract results

**Actual API response:**
```json
{
  "status_code": 200,
  "headers": {...},
  "body": "<!doctype html><html itemscope=\"\" itemtype=\"http://schema.org/SearchResultsPage\">..."
}
```

**What SDK expects:**
```json
{
  "organic": [
    {
      "title": "Python Programming",
      "url": "https://...",
      "description": "..."
    }
  ],
  "ads": [...],
  "featured_snippet": {...}
}
```

### Impact

- **Severity:** Critical - SERP API is completely non-functional
- **Affected functionality:** All SERP API searches (Google, Bing, Yandex)
- **User impact:** SERP features advertised in README don't work at all
- **Discovery:** Found when running `test_04_serp_google.py`

### Root Cause Analysis

The SDK has fundamental misunderstandings about how Bright Data's SERP API works:

1. **Wrong endpoint**: The SDK uses `/request` endpoint with `payload = {"zone": zone, "url": search_url, "format": "json", "method": "GET"}`. This is the Web Unlocker API format, not SERP API.

2. **SERP zones work differently**: SERP zones (`type: serp`) return raw HTML responses wrapped in HTTP response structure. They're designed to fetch search results HTML, not parse it.

3. **Missing parsing layer**: Other SERP SDKs either:
   - Use a different endpoint that returns parsed data
   - Include HTML parsers to extract structured data from raw HTML
   - Use Bright Data's parsing service (if available)

### Testing

```bash
python probe_tests/test_04_serp_google.py
# Shows HTML being returned in body field
```

### Solution Options

1. **Find correct SERP endpoint**: Bright Data might have a `/serp` or similar endpoint that returns parsed results
2. **Add HTML parsing**: Use BeautifulSoup or similar to parse Google/Bing/Yandex HTML
3. **Use different zone type**: There might be a parsed SERP zone type
4. **Add parser parameter**: Maybe `{"parser": true}` or similar enables parsing

### Current Workaround

None - SERP API is non-functional in current SDK implementation

---

## Issue 6: SDK Expects Parsed SERP Data But API Returns Raw HTML

**File:** `src/brightdata/api/serp/data_normalizer.py` (Line 78+)

### What is the issue?

The SDK's GoogleDataNormalizer expects the SERP API to return parsed JSON with specific fields, but the API actually returns raw HTML.

**SDK expects (data_normalizer.py lines 78-105):**
```python
# Line 78: Expects 'organic' field with search results
organic = data.get("organic", [])

# Lines 80-87: Expects each result to have these fields
for i, item in enumerate(organic, 1):
    results.append({
        "position": i,
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "description": item.get("description", ""),
        "displayed_url": item.get("displayed_url", ""),
    })

# Lines 91-105: Expects these optional fields
"total_results": data.get("total_results")
"search_information": data.get("search_information", {})
"featured_snippet": data.get("featured_snippet")
"knowledge_panel": data.get("knowledge_panel")
"people_also_ask": data.get("people_also_ask")
"related_searches": data.get("related_searches")
"ads": data.get("ads")
```

**API actually returns:**
```json
{
  "status_code": 200,
  "headers": {...},
  "body": "<!doctype html><html>..." // Raw HTML, no parsed fields
}
```

### Impact

- **Severity:** Critical
- **Affected functionality:** All SERP normalizers expect parsed data
- **User impact:** SERP API always returns 0 results because normalizer can't find expected fields
- **Discovery:** Found in `src/brightdata/api/serp/data_normalizer.py`

### Root Cause

The SDK was designed assuming the SERP API would return parsed/structured JSON data with fields like `organic`, `ads`, `featured_snippet`, etc. However, Bright Data's SERP zones return raw HTML that needs to be parsed to extract these fields.

### Testing

Running the test shows the mismatch:
```bash
python probe_tests/test_04_serp_google.py
# Debug output shows: "SERP API returned JSON with keys: ['status_code', 'headers', 'body']"
# Not the expected: ['organic', 'ads', 'featured_snippet', ...]
```

