"""Example: Using Bright Data SDK with pandas for data analysis.

This example demonstrates how to integrate the SDK with pandas for
data science workflows, including batch scraping, DataFrame operations,
visualization, and exporting results.
"""

import pandas as pd
import matplotlib.pyplot as plt
from brightdata import BrightDataClient


def example_single_result_to_dataframe():
    """Convert a single scrape result to a pandas DataFrame."""
    print("=" * 70)
    print("EXAMPLE 1: Single Result to DataFrame")
    print("=" * 70)

    client = BrightDataClient()

    # Scrape a product
    result = client.scrape.amazon.products(url="https://www.amazon.com/dp/B0CRMZHDG8")

    if result.success and result.data:
        # Convert to DataFrame
        df = pd.DataFrame([result.data])

        # Add metadata columns
        df["url"] = result.url
        df["cost"] = result.cost
        df["elapsed_ms"] = result.elapsed_ms()
        df["scraped_at"] = pd.Timestamp.now()

        print(f"\n✅ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
        print("\nFirst few columns:")
        print(df[["title", "final_price", "rating", "cost"]].head())

        return df
    else:
        print(f"❌ Scrape failed: {result.error}")
        return None


def example_batch_scraping_to_dataframe():
    """Scrape multiple products and create a comprehensive DataFrame."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 2: Batch Scraping to DataFrame")
    print("=" * 70)

    client = BrightDataClient()

    # List of product URLs
    urls = [
        "https://www.amazon.com/dp/B0CRMZHDG8",
        "https://www.amazon.com/dp/B09B9C8K3T",
        "https://www.amazon.com/dp/B0CX23V2ZK",
    ]

    # Scrape all products
    print(f"\nScraping {len(urls)} products...")
    results = []

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url}")
        try:
            result = client.scrape.amazon.products(url=url)

            if result.success:
                results.append(
                    {
                        "url": result.url,
                        "title": result.data.get("title", "N/A"),
                        "price": result.data.get("final_price", "N/A"),
                        "rating": result.data.get("rating", "N/A"),
                        "reviews_count": result.data.get("reviews_count", 0),
                        "availability": result.data.get("availability", "N/A"),
                        "cost": result.cost,
                        "elapsed_ms": result.elapsed_ms(),
                        "status": "success",
                    }
                )
            else:
                results.append({"url": url, "error": result.error, "status": "failed"})
        except Exception as e:
            results.append({"url": url, "error": str(e), "status": "error"})

    # Create DataFrame
    df = pd.DataFrame(results)

    print(f"\n✅ Created DataFrame with {len(df)} rows")
    print(f"   Success: {(df['status'] == 'success').sum()}")
    print(f"   Failed: {(df['status'] != 'success').sum()}")
    print(f"   Total cost: ${df[df['status'] == 'success']['cost'].sum():.4f}")

    print("\nDataFrame:")
    print(df[["title", "price", "rating", "cost", "status"]])

    return df


def example_data_analysis(df: pd.DataFrame):
    """Perform analysis on scraped data."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 3: Data Analysis")
    print("=" * 70)

    # Filter successful scrapes
    df_success = df[df["status"] == "success"].copy()

    if len(df_success) == 0:
        print("❌ No successful scrapes to analyze")
        return

    # Clean numeric columns
    df_success["price_clean"] = (
        df_success["price"]
        .astype(str)
        .str.replace("$", "")
        .str.replace(",", "")
        .str.extract(r"([\d.]+)", expand=False)
        .astype(float)
    )

    df_success["rating_clean"] = (
        df_success["rating"].astype(str).str.extract(r"([\d.]+)", expand=False).astype(float)
    )

    # Descriptive statistics
    print("\n📊 Price Statistics:")
    print(df_success["price_clean"].describe())

    print("\n⭐ Rating Statistics:")
    print(df_success["rating_clean"].describe())

    print("\n⏱️  Performance Statistics:")
    print(f"  Avg scraping time: {df_success['elapsed_ms'].mean():.2f}ms")
    print(f"  Min scraping time: {df_success['elapsed_ms'].min():.2f}ms")
    print(f"  Max scraping time: {df_success['elapsed_ms'].max():.2f}ms")

    print("\n💰 Cost Analysis:")
    print(f"  Total cost: ${df_success['cost'].sum():.4f}")
    print(f"  Avg cost per product: ${df_success['cost'].mean():.4f}")

    return df_success


def example_visualization(df: pd.DataFrame):
    """Create visualizations from the data."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 4: Data Visualization")
    print("=" * 70)

    if "price_clean" not in df.columns or "rating_clean" not in df.columns:
        print("❌ Missing required columns for visualization")
        return

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Price distribution
    axes[0, 0].hist(df["price_clean"].dropna(), bins=10, edgecolor="black", color="blue", alpha=0.7)
    axes[0, 0].set_title("Price Distribution", fontsize=14, fontweight="bold")
    axes[0, 0].set_xlabel("Price ($)")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].grid(axis="y", alpha=0.3)

    # Rating distribution
    axes[0, 1].hist(
        df["rating_clean"].dropna(), bins=10, edgecolor="black", color="green", alpha=0.7
    )
    axes[0, 1].set_title("Rating Distribution", fontsize=14, fontweight="bold")
    axes[0, 1].set_xlabel("Rating (stars)")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].grid(axis="y", alpha=0.3)

    # Price vs Rating scatter
    axes[1, 0].scatter(df["price_clean"], df["rating_clean"], alpha=0.6, s=100, color="purple")
    axes[1, 0].set_title("Price vs Rating", fontsize=14, fontweight="bold")
    axes[1, 0].set_xlabel("Price ($)")
    axes[1, 0].set_ylabel("Rating (stars)")
    axes[1, 0].grid(alpha=0.3)

    # Scraping performance
    axes[1, 1].bar(range(len(df)), df["elapsed_ms"], color="orange", alpha=0.7)
    axes[1, 1].set_title("Scraping Performance", fontsize=14, fontweight="bold")
    axes[1, 1].set_xlabel("Product Index")
    axes[1, 1].set_ylabel("Time (ms)")
    axes[1, 1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("amazon_analysis.png", dpi=150, bbox_inches="tight")
    print("\n✅ Visualization saved to amazon_analysis.png")

    # Uncomment to display plot
    # plt.show()


def example_export_results(df: pd.DataFrame):
    """Export DataFrame to various formats."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 5: Export Results")
    print("=" * 70)

    # Export to CSV
    csv_file = "amazon_products_analysis.csv"
    df.to_csv(csv_file, index=False)
    print(f"✅ Exported to {csv_file}")

    # Export to Excel with multiple sheets
    excel_file = "amazon_products_analysis.xlsx"
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        # Main data
        df.to_excel(writer, sheet_name="Products", index=False)

        # Summary statistics
        summary = pd.DataFrame(
            {
                "Metric": [
                    "Total Products",
                    "Successful Scrapes",
                    "Failed Scrapes",
                    "Total Cost",
                    "Avg Time (ms)",
                ],
                "Value": [
                    len(df),
                    (df["status"] == "success").sum(),
                    (df["status"] != "success").sum(),
                    f"${df[df['status'] == 'success']['cost'].sum():.4f}",
                    f"{df[df['status'] == 'success']['elapsed_ms'].mean():.2f}",
                ],
            }
        )
        summary.to_excel(writer, sheet_name="Summary", index=False)

    print(f"✅ Exported to {excel_file} (with multiple sheets)")

    # Export to JSON
    json_file = "amazon_products_analysis.json"
    df.to_json(json_file, orient="records", indent=2)
    print(f"✅ Exported to {json_file}")

    import os

    print("\n📁 File Sizes:")
    print(f"  CSV: {os.path.getsize(csv_file) / 1024:.2f} KB")
    print(f"  Excel: {os.path.getsize(excel_file) / 1024:.2f} KB")
    print(f"  JSON: {os.path.getsize(json_file) / 1024:.2f} KB")


def example_advanced_pandas_operations():
    """Demonstrate advanced pandas operations with SDK data."""
    print("\n\n" + "=" * 70)
    print("EXAMPLE 6: Advanced Pandas Operations")
    print("=" * 70)

    client = BrightDataClient()

    # Create sample data
    data = {
        "asin": ["B001", "B002", "B003"],
        "title": ["Product A", "Product B", "Product C"],
        "price": ["$29.99", "$49.99", "$19.99"],
        "rating": [4.5, 4.8, 4.2],
        "category": ["Electronics", "Electronics", "Home"],
    }
    df = pd.DataFrame(data)

    # 1. Filtering
    print("\n1️⃣  Filtering products with rating > 4.3:")
    high_rated = df[df["rating"] > 4.3]
    print(high_rated[["title", "rating"]])

    # 2. Grouping
    print("\n2️⃣  Group by category:")
    by_category = (
        df.groupby("category")
        .agg({"rating": "mean", "asin": "count"})
        .rename(columns={"asin": "count"})
    )
    print(by_category)

    # 3. Sorting
    print("\n3️⃣  Sort by rating (descending):")
    sorted_df = df.sort_values("rating", ascending=False)
    print(sorted_df[["title", "rating"]])

    # 4. Adding calculated columns
    print("\n4️⃣  Adding calculated columns:")
    df["price_numeric"] = df["price"].str.replace("$", "").astype(float)
    df["value_score"] = df["rating"] / df["price_numeric"]  # Higher is better value
    print(df[["title", "rating", "price_numeric", "value_score"]])

    # 5. Pivot tables
    print("\n5️⃣  Pivot table:")
    pivot = df.pivot_table(values="rating", index="category", aggfunc=["mean", "count"])
    print(pivot)


def main():
    """Run all pandas integration examples."""
    print("\n" + "=" * 70)
    print("PANDAS INTEGRATION EXAMPLES")
    print("=" * 70)

    try:
        # Example 1: Single result
        single_df = example_single_result_to_dataframe()

        # Example 2: Batch scraping
        batch_df = example_batch_scraping_to_dataframe()

        # Example 3: Data analysis
        if batch_df is not None and len(batch_df) > 0:
            analyzed_df = example_data_analysis(batch_df)

            # Example 4: Visualization
            if analyzed_df is not None and len(analyzed_df) > 0:
                example_visualization(analyzed_df)

            # Example 5: Export
            example_export_results(batch_df)

        # Example 6: Advanced operations
        example_advanced_pandas_operations()

        print("\n\n" + "=" * 70)
        print("✅ ALL PANDAS EXAMPLES COMPLETED")
        print("=" * 70)
        print("\n📚 Key Takeaways:")
        print("  1. Convert SDK results to DataFrames for analysis")
        print("  2. Use batch scraping for multiple products")
        print("  3. Leverage pandas for data cleaning and statistics")
        print("  4. Create visualizations with matplotlib")
        print("  5. Export to CSV, Excel, and JSON formats")
        print("\n💡 Pro Tips:")
        print("  - Use tqdm for progress bars")
        print("  - Cache results with joblib during development")
        print("  - Track costs to stay within budget")
        print("  - Save checkpoints for long-running scrapes")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
