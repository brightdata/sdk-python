"""
Amazon product data schemas.

Dataclasses for typed access to Amazon scraper results.
These are optional - you can still use dict access via result.data.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SubcategoryRank:
    """Amazon subcategory ranking info."""

    subcategory_name: str | None = None
    subcategory_rank: int | None = None


@dataclass
class ProductDetail:
    """Product detail key-value pair."""

    type: str | None = None
    value: str | None = None


@dataclass
class OtherSellerPrice:
    """Price from other sellers."""

    price: float | None = None
    price_per_unit: float | None = None
    unit: str | None = None
    seller_name: str | None = None
    seller_url: str | None = None


@dataclass
class CustomersSay:
    """Customer sentiment keywords."""

    keywords: dict[str, Any] | None = None


@dataclass
class AmazonProductResult:
    """
    Complete Amazon product data from scraper.

    All 74 fields returned by the Amazon product scraper.
    All fields are optional since not all products have all data.

    Example:
        >>> result = await client.scrape.amazon.products(url="...")
        >>> if result.success and result.data:
        ...     product = AmazonProductResult.from_dict(result.data)
        ...     print(product.title)
        ...     print(product.rating)
    """

    # Basic product info
    title: str | None = None
    brand: str | None = None
    description: str | None = None
    manufacturer: str | None = None
    department: str | None = None
    model_number: str | None = None

    # Identifiers
    asin: str | None = None
    parent_asin: str | None = None
    upc: str | None = None

    # URLs
    url: str | None = None
    domain: str | None = None
    image_url: str | None = None
    image: str | None = None
    seller_url: str | None = None
    store_url: str | None = None

    # Pricing
    currency: str | None = None
    final_price_high: float | None = None
    prices_breakdown: list[dict[str, Any]] | None = None
    other_sellers_prices: list[dict[str, Any]] | None = None
    coupon: str | None = None
    coupon_description: str | None = None

    # Ratings and reviews
    rating: float | None = None
    reviews_count: int | None = None
    top_review: str | None = None
    customer_says: str | None = None
    customers_say: dict[str, Any] | None = None
    answered_questions: int | None = None

    # Seller info
    seller_name: str | None = None
    seller_id: str | None = None
    number_of_sellers: int | None = None
    ships_from: str | None = None
    buybox_seller_rating: float | None = None
    inactive_buy_box: bool | None = None

    # Categories and rankings
    categories: list[str] | None = None
    root_bs_category: str | None = None
    bs_category: str | None = None
    root_bs_rank: int | None = None
    bs_rank: int | None = None
    subcategory_rank: list[dict[str, Any]] | None = None

    # Product details
    features: list[str] | None = None
    product_details: list[dict[str, Any]] | None = None
    product_description: list[dict[str, Any]] | None = None
    product_dimensions: str | None = None
    item_weight: str | None = None
    country_of_origin: str | None = None
    date_first_available: str | None = None
    language: str | None = None

    # Media
    images: list[str] | None = None
    images_count: int | None = None
    video: bool | None = None
    videos: list[str] | None = None
    video_count: int | None = None
    downloadable_videos: list[str] | None = None

    # Availability and badges
    is_available: bool | None = None
    max_quantity_available: int | None = None
    amazon_choice: bool | None = None
    amazon_prime: bool | None = None
    badge: str | None = None
    all_badges: list[str] | None = None
    premium_brand: bool | None = None
    climate_pledge_friendly: bool | None = None

    # Additional content
    plus_content: bool | None = None
    from_the_brand: list[str] | None = None
    editorial_reviews: str | None = None
    about_the_author: str | None = None
    sustainability_features: str | None = None
    return_policy: str | None = None
    variations_values: dict[str, Any] | None = None

    # Location
    zipcode: str | None = None
    city: str | None = None

    # Sponsored/advertising
    sponsored: bool | None = None
    sponsered: bool | None = None  # Note: typo exists in API response

    # Metadata
    timestamp: str | None = None
    input: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AmazonProductResult":
        """
        Create AmazonProductResult from dictionary.

        Args:
            data: Dictionary from result.data

        Returns:
            AmazonProductResult instance with all available fields

        Example:
            >>> product = AmazonProductResult.from_dict(result.data)
        """
        # Get all field names from the dataclass
        field_names = {f.name for f in cls.__dataclass_fields__.values()}

        # Filter data to only include known fields
        filtered_data = {k: v for k, v in data.items() if k in field_names}

        return cls(**filtered_data)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary, excluding None values.

        Returns:
            Dictionary with non-None field values
        """
        from dataclasses import asdict

        return {k: v for k, v in asdict(self).items() if v is not None}
