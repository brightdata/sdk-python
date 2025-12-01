#!/usr/bin/env python3
"""Get dataset metadata to understand correct input parameters."""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from brightdata import BrightDataClient


async def get_metadata(dataset_id: str, name: str):
    """Fetch and display dataset metadata."""

    print(f"\n{'=' * 60}")
    print(f"{name} - Dataset Metadata")
    print(f"Dataset ID: {dataset_id}")
    print(f"{'=' * 60}")

    client = BrightDataClient()

    async with client.engine:
        try:
            url = f"{client.engine.BASE_URL}/datasets/{dataset_id}/metadata"

            async with client.engine.get_from_url(url) as response:
                if response.status == 200:
                    data = await response.json()

                    print("\n✅ Got metadata!")

                    # Display input schema
                    if "input_schema" in data:
                        print("\n📋 INPUT SCHEMA:")
                        print(json.dumps(data["input_schema"], indent=2))

                    # Display other useful info
                    if "name" in data:
                        print(f"\nName: {data['name']}")
                    if "description" in data:
                        print(f"Description: {data['description'][:200]}...")

                else:
                    error_text = await response.text()
                    print(f"\n❌ API call failed (HTTP {response.status})")
                    print(f"Error: {error_text}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Get metadata for key datasets."""

    datasets = [
        ("gd_l7q7dkf244hwjntr0", "Amazon Products"),
        ("gd_le8e811kzy4ggddlq", "Amazon Reviews"),
        ("gd_l1viktl72bvl7bjuj0", "LinkedIn Profiles"),
        ("gd_l1vikfnt1wgvvqz95w", "LinkedIn Companies"),
        ("gd_lpfll7v5hcqtkxl6l", "LinkedIn Jobs"),
        ("gd_l1vikfch901nx3by4", "Instagram Profiles"),
        ("gd_lk5ns7kz21pck8jpis", "Instagram Posts"),
        ("gd_lkaxegm826bjpoo9m5", "Facebook Posts by Profile"),
    ]

    for dataset_id, name in datasets:
        await get_metadata(dataset_id, name)
        await asyncio.sleep(0.5)  # Rate limiting


if __name__ == "__main__":
    asyncio.run(main())
