"""
Amazon product data schemas.

Dataclasses for typed access to Amazon scraper results.
These are optional - you can still use dict access via result.data.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class SubcategoryRank:
    """Amazon subcategory ranking info."""

    subcategory_name: Optional[str] = None
    subcategory_rank: Optional[int] = None


@dataclass
class ProductDetail:
    """Product detail key-value pair."""

    type: Optional[str] = None
    value: Optional[str] = None


@dataclass
class OtherSellerPrice:
    """Price from other sellers."""

    price: Optional[float] = None
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
    seller_name: Optional[str] = None
    seller_url: Optional[str] = None


@dataclass
class CustomersSay:
    """Customer sentiment keywords."""

    keywords: Optional[Dict[str, Any]] = None


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
    title: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    department: Optional[str] = None
    model_number: Optional[str] = None

    # Identifiers
    asin: Optional[str] = None
    parent_asin: Optional[str] = None
    upc: Optional[str] = None

    # URLs
    url: Optional[str] = None
    domain: Optional[str] = None
    image_url: Optional[str] = None
    image: Optional[str] = None
    seller_url: Optional[str] = None
    store_url: Optional[str] = None

    # Pricing
    currency: Optional[str] = None
    final_price_high: Optional[float] = None
    prices_breakdown: Optional[List[Dict[str, Any]]] = None
    other_sellers_prices: Optional[List[Dict[str, Any]]] = None
    coupon: Optional[str] = None
    coupon_description: Optional[str] = None

    # Ratings and reviews
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    top_review: Optional[str] = None
    customer_says: Optional[str] = None
    customers_say: Optional[Dict[str, Any]] = None
    answered_questions: Optional[int] = None

    # Seller info
    seller_name: Optional[str] = None
    seller_id: Optional[str] = None
    number_of_sellers: Optional[int] = None
    ships_from: Optional[str] = None
    buybox_seller_rating: Optional[float] = None
    inactive_buy_box: Optional[bool] = None

    # Categories and rankings
    categories: Optional[List[str]] = None
    root_bs_category: Optional[str] = None
    bs_category: Optional[str] = None
    root_bs_rank: Optional[int] = None
    bs_rank: Optional[int] = None
    subcategory_rank: Optional[List[Dict[str, Any]]] = None

    # Product details
    features: Optional[List[str]] = None
    product_details: Optional[List[Dict[str, Any]]] = None
    product_description: Optional[List[Dict[str, Any]]] = None
    product_dimensions: Optional[str] = None
    item_weight: Optional[str] = None
    country_of_origin: Optional[str] = None
    date_first_available: Optional[str] = None
    language: Optional[str] = None

    # Media
    images: Optional[List[str]] = None
    images_count: Optional[int] = None
    video: Optional[bool] = None
    videos: Optional[List[str]] = None
    video_count: Optional[int] = None
    downloadable_videos: Optional[List[str]] = None

    # Availability and badges
    is_available: Optional[bool] = None
    max_quantity_available: Optional[int] = None
    amazon_choice: Optional[bool] = None
    amazon_prime: Optional[bool] = None
    badge: Optional[str] = None
    all_badges: Optional[List[str]] = None
    premium_brand: Optional[bool] = None
    climate_pledge_friendly: Optional[bool] = None

    # Additional content
    plus_content: Optional[bool] = None
    from_the_brand: Optional[List[str]] = None
    editorial_reviews: Optional[str] = None
    about_the_author: Optional[str] = None
    sustainability_features: Optional[str] = None
    return_policy: Optional[str] = None
    variations_values: Optional[Dict[str, Any]] = None

    # Location
    zipcode: Optional[str] = None
    city: Optional[str] = None

    # Sponsored/advertising
    sponsored: Optional[bool] = None
    sponsered: Optional[bool] = None  # Note: typo exists in API response

    # Metadata
    timestamp: Optional[str] = None
    input: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AmazonProductResult":
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary, excluding None values.

        Returns:
            Dictionary with non-None field values
        """
        from dataclasses import asdict

        return {k: v for k, v in asdict(self).items() if v is not None}
