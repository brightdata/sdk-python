"""Bright Search examples using the configured Bright Data API key.

Run this file to make one Company search. The other functions demonstrate
People and structured E-commerce search when called explicitly.
"""

import asyncio

from brightdata import BrightDataClient, BrightSearchPage, SyncBrightDataClient


async def company_search() -> BrightSearchPage:
    """Make one request, leaving paging and recovery under caller control."""
    async with BrightDataClient(auto_create_zones=False) as client:
        page = await client.search.business.companies(
            "US software companies with 50 to 500 employees",
            mode="instant",
            view="summary",
            limit=10,
        )
    print(f"Request: {page.req_id}")
    print(f"Reached: {page.meta['matched']}; coverage: {page.meta['coverage_percent']}%")
    for document in page.documents:
        print(document["bright_id"], document["data"].get("name"))
    return page


def people_search_sync() -> BrightSearchPage:
    """Use the same page contract from an ordinary synchronous script."""
    with SyncBrightDataClient(auto_create_zones=False) as client:
        return client.search.business.people(
            "Product managers in the United States",
            mode="instant",
            view={"fields": ["name", "current_title", "url"]},
        )


async def product_search() -> BrightSearchPage:
    """Send the native structured query without a separate query-builder API."""
    async with BrightDataClient(auto_create_zones=False) as client:
        return await client.search.ecommerce.products(
            query={
                "and": [
                    {"equals": {"retailer": "Argos"}},
                    {"equals": {"sku": "4326522"}},
                ]
            },
            mode="ludicrous",
            view="full",
        )


if __name__ == "__main__":
    asyncio.run(company_search())
