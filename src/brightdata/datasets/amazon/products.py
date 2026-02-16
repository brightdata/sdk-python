"""
Amazon Products dataset.

Dataset ID: gd_l7q7dkf244hwjntr0

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AmazonProducts(BaseDataset):
    """
    Amazon Products dataset.

    Access Amazon product records with filtering.

    Example:
        >>> products = client.datasets.amazon_products
        >>> metadata = await products.get_metadata()
        >>> snapshot_id = await products.filter(
        ...     filter={"name": "rating", "operator": ">", "value": 4.5},
        ...     records_limit=100
        ... )
        >>> data = await products.download(snapshot_id)
    """

    DATASET_ID = "gd_l7q7dkf244hwjntr0"
    NAME = "amazon_products"

    # All available fields with metadata
    # Format: field_name -> {"type": str, "description": str}
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Core product identification
        "title": {
            "type": "text",
            "description": "Product title/name",
        },
        "asin": {
            "type": "text",
            "description": "Amazon Standard Identification Number",
        },
        "parent_asin": {
            "type": "text",
            "description": "Parent ASIN for product variations",
        },
        "input_asin": {
            "type": "text",
            "description": "Original input ASIN used for scraping",
        },
        "url": {
            "type": "url",
            "description": "Full product page URL",
        },
        "origin_url": {
            "type": "url",
            "description": "Original source URL",
        },
        "domain": {
            "type": "text",
            "description": "Amazon domain (e.g., amazon.com)",
        },
        # Brand & seller
        "brand": {
            "type": "text",
            "description": "Product brand name",
        },
        "seller_name": {
            "type": "text",
            "description": "Name of the seller",
        },
        "seller_id": {
            "type": "text",
            "description": "Unique seller identifier",
        },
        "seller_url": {
            "type": "url",
            "description": "URL to seller's storefront",
        },
        "manufacturer": {
            "type": "text",
            "description": "Product manufacturer",
        },
        "buybox_seller": {
            "type": "text",
            "description": "Current Buy Box winner seller",
        },
        "number_of_sellers": {
            "type": "number",
            "description": "Number of sellers offering this product",
        },
        "buybox_seller_rating": {
            "type": "number",
            "description": "Buy Box seller's rating",
        },
        # Pricing
        "initial_price": {
            "type": "number",
            "description": "Original/list price",
        },
        "final_price": {
            "type": "number",
            "description": "Current selling price",
        },
        "final_price_high": {
            "type": "number",
            "description": "High end of price range (for variations)",
        },
        "currency": {
            "type": "text",
            "description": "Price currency code (e.g., USD)",
        },
        "discount": {
            "type": "text",
            "description": "Discount percentage or amount",
        },
        "buybox_prices": {
            "type": "object",
            "description": "Buy Box pricing details",
        },
        "prices_breakdown": {
            "type": "object",
            "description": "Detailed price breakdown (list, deal, typical)",
        },
        "other_sellers_prices": {
            "type": "array",
            "description": "Prices from other sellers",
        },
        "coupon": {
            "type": "text",
            "description": "Available coupon code",
        },
        "coupon_description": {
            "type": "text",
            "description": "Description of coupon discount",
        },
        "inactive_buy_box": {
            "type": "object",
            "description": "Inactive Buy Box information",
        },
        # Availability & shipping
        "availability": {
            "type": "text",
            "description": "Stock availability status",
        },
        "is_available": {
            "type": "boolean",
            "description": "Whether product is currently available",
        },
        "max_quantity_available": {
            "type": "number",
            "description": "Maximum quantity available for purchase",
        },
        "delivery": {
            "type": "array",
            "description": "Delivery options and dates",
        },
        "ships_from": {
            "type": "text",
            "description": "Shipping origin location",
        },
        "zipcode": {
            "type": "text",
            "description": "Delivery zipcode context",
        },
        "city": {
            "type": "text",
            "description": "Delivery city context",
        },
        "return_policy": {
            "type": "text",
            "description": "Return policy description",
        },
        # Ratings & reviews
        "rating": {
            "type": "number",
            "description": "Average star rating (0-5)",
        },
        "reviews_count": {
            "type": "number",
            "description": "Total number of customer reviews",
        },
        "answered_questions": {
            "type": "number",
            "description": "Number of answered Q&A",
        },
        "top_review": {
            "type": "text",
            "description": "Featured/top customer review",
        },
        "customer_says": {
            "type": "text",
            "description": "AI-generated customer sentiment summary",
        },
        "customers_say": {
            "type": "object",
            "description": "Detailed customer feedback analysis",
        },
        # Categories & rankings
        "categories": {
            "type": "array",
            "description": "Product category hierarchy",
        },
        "root_bs_category": {
            "type": "text",
            "description": "Root best seller category",
        },
        "bs_category": {
            "type": "text",
            "description": "Best seller subcategory",
        },
        "root_bs_rank": {
            "type": "number",
            "description": "Best seller rank in root category",
        },
        "bs_rank": {
            "type": "number",
            "description": "Best seller rank in subcategory",
        },
        "subcategory_rank": {
            "type": "array",
            "description": "Rankings in subcategories",
        },
        "department": {
            "type": "text",
            "description": "Product department",
        },
        # Badges & features
        "badge": {
            "type": "text",
            "description": "Product badge (e.g., Best Seller)",
        },
        "all_badges": {
            "type": "array",
            "description": "All product badges",
        },
        "amazon_choice": {
            "type": "boolean",
            "description": "Whether product is Amazon's Choice",
        },
        "amazon_prime": {
            "type": "boolean",
            "description": "Whether eligible for Prime",
        },
        "premium_brand": {
            "type": "boolean",
            "description": "Whether a premium brand",
        },
        "climate_pledge_friendly": {
            "type": "boolean",
            "description": "Climate Pledge Friendly certification",
        },
        "sustainability_features": {
            "type": "array",
            "description": "Sustainability certifications and features",
        },
        "sponsored": {
            "type": "boolean",
            "description": "Whether product listing is sponsored",
        },
        # Product details
        "description": {
            "type": "text",
            "description": "Short product description",
        },
        "product_description": {
            "type": "text",
            "description": "Full product description",
        },
        "features": {
            "type": "array",
            "description": "Product feature bullet points",
        },
        "product_details": {
            "type": "array",
            "description": "Technical product specifications",
        },
        "product_dimensions": {
            "type": "text",
            "description": "Product size dimensions",
        },
        "item_weight": {
            "type": "text",
            "description": "Product weight",
        },
        "model_number": {
            "type": "text",
            "description": "Manufacturer model number",
        },
        "upc": {
            "type": "text",
            "description": "Universal Product Code",
        },
        "ISBN10": {
            "type": "text",
            "description": "ISBN-10 for books",
        },
        "ingredients": {
            "type": "text",
            "description": "Product ingredients (for applicable items)",
        },
        "country_of_origin": {
            "type": "text",
            "description": "Country where product is made",
        },
        "date_first_available": {
            "type": "text",
            "description": "Date product was first listed",
        },
        "format": {
            "type": "text",
            "description": "Product format (for media items)",
        },
        "language": {
            "type": "text",
            "description": "Product language",
        },
        # Images & media
        "image": {
            "type": "url",
            "description": "Main product image URL",
        },
        "image_url": {
            "type": "url",
            "description": "Primary image URL",
        },
        "images": {
            "type": "array",
            "description": "All product image URLs",
        },
        "images_count": {
            "type": "number",
            "description": "Number of product images",
        },
        "video": {
            "type": "url",
            "description": "Product video URL",
        },
        "videos": {
            "type": "array",
            "description": "All product video URLs",
        },
        "video_count": {
            "type": "number",
            "description": "Number of product videos",
        },
        "downloadable_videos": {
            "type": "array",
            "description": "Downloadable video URLs",
        },
        # Variations
        "variations": {
            "type": "array",
            "description": "Product variations (size, color, etc.)",
        },
        "variations_values": {
            "type": "array",
            "description": "Available variation options",
        },
        # Enhanced content
        "plus_content": {
            "type": "boolean",
            "description": "Whether has A+ Content",
        },
        "from_the_brand": {
            "type": "array",
            "description": "Brand story/content section",
        },
        "editorial_reviews": {
            "type": "array",
            "description": "Editorial review content",
        },
        "about_the_author": {
            "type": "text",
            "description": "Author bio (for books)",
        },
        # Store & purchase info
        "store_url": {
            "type": "url",
            "description": "Brand store URL",
        },
        "bought_past_month": {
            "type": "number",
            "description": "Units sold in past month",
        },
    }

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)

    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names."""
        return list(cls.FIELDS.keys())

    @classmethod
    def get_fields_by_type(cls, field_type: str) -> list:
        """Get fields of a specific type (text, number, array, object, url, boolean)."""
        return [name for name, info in cls.FIELDS.items() if info.get("type") == field_type]

    @classmethod
    def get_pricing_fields(cls) -> list:
        """Get all pricing-related fields."""
        pricing_keywords = ["price", "cost", "discount", "coupon"]
        return [
            name for name in cls.FIELDS.keys() if any(kw in name.lower() for kw in pricing_keywords)
        ]
