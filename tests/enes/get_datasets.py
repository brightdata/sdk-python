#!/usr/bin/env python3
"""Get list of available datasets from Bright Data API."""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def get_datasets():
    """Fetch and display available datasets."""

    print("=" * 60)
    print("BRIGHT DATA - Available Datasets")
    print("=" * 60)

    client = BrightDataClient()

    async with client.engine:
        print("\n🔍 Fetching dataset list from API...")

        try:
            # Make API call to get dataset list
            url = f"{client.engine.BASE_URL}/datasets/list"
            print(f"📡 URL: {url}")

            async with client.engine.get_from_url(url) as response:
                if response.status == 200:
                    data = await response.json()

                    print("\n✅ Got response!")
                    print(f"📊 Response type: {type(data)}")

                    if isinstance(data, list):
                        print(f"📋 Found {len(data)} datasets\n")

                        # Group by platform
                        platforms = {}
                        for dataset in data:
                            name = dataset.get("name", "unknown")
                            dataset_id = dataset.get("id", "unknown")

                            # Extract platform from name
                            platform = name.split("_")[0] if "_" in name else name

                            if platform not in platforms:
                                platforms[platform] = []
                            platforms[platform].append({"name": name, "id": dataset_id})

                        # Display grouped results
                        for platform, datasets in sorted(platforms.items()):
                            print(f"\n🔹 {platform.upper()}")
                            for ds in datasets:
                                print(f"   {ds['name']}: {ds['id']}")

                    elif isinstance(data, dict):
                        print("\n📦 Response data:")
                        import json

                        print(json.dumps(data, indent=2))

                    else:
                        print("\n⚠️  Unexpected response format")
                        print(f"Data: {data}")

                else:
                    error_text = await response.text()
                    print(f"\n❌ API call failed (HTTP {response.status})")
                    print(f"Error: {error_text}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(get_datasets())
