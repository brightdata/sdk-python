"""
Crunchbase Companies dataset.

Dataset ID: gd_l1vijqt9jfj7olije
Records: 2.3M+ companies

See FIELDS dict for all filterable fields with descriptions and fill rates.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class CrunchbaseCompanies(BaseDataset):
    """
    Crunchbase Companies dataset.

    Access 2.3M+ Crunchbase company records with filtering.

    Example:
        >>> companies = client.datasets.crunchbase_companies
        >>> metadata = await companies.get_metadata()
        >>> snapshot_id = await companies.filter(
        ...     filter={"name": "num_employees", "operator": ">", "value": 100},
        ...     records_limit=100
        ... )
        >>> data = await companies.download(snapshot_id)
    """

    DATASET_ID = "gd_l1vijqt9jfj7olije"
    NAME = "crunchbase_companies"

    # All available fields with metadata
    # Format: field_name -> {"type": str, "description": str, "fill_rate": float}
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Core identification
        "name": {
            "type": "text",
            "description": "The name of the company",
            "fill_rate": 100.00,
        },
        "url": {
            "type": "url",
            "description": "The URL or web address associated with the company",
            "fill_rate": 100.00,
        },
        "id": {
            "type": "text",
            "description": "A unique identifier for each company in Crunchbase",
            "fill_rate": 100.00,
        },
        "uuid": {
            "type": "text",
            "description": "Universally unique identifier for the company",
            "fill_rate": 100.00,
        },
        "company_id": {
            "type": "text",
            "description": "A unique identifier for each company in Crunchbase",
            "fill_rate": 99.07,
        },
        "type": {
            "type": "text",
            "description": "Type of data entry",
            "fill_rate": 100.00,
        },
        # Company info
        "about": {
            "type": "text",
            "description": "Overview or description of the company",
            "fill_rate": 100.00,
        },
        "full_description": {
            "type": "text",
            "description": "Detailed description of the company",
            "fill_rate": 100.00,
        },
        "company_overview": {
            "type": "text",
            "description": "Overview or description of the company",
            "fill_rate": 99.07,
        },
        "legal_name": {
            "type": "text",
            "description": "Legal name of the company",
            "fill_rate": 59.62,
        },
        "cb_rank": {
            "type": "number",
            "description": "Crunchbase rank assigned to the company",
            "fill_rate": 97.02,
        },
        "image": {
            "type": "url",
            "description": "Image or logo associated with the company",
            "fill_rate": 94.22,
        },
        # Status & type
        "operating_status": {
            "type": "text",
            "description": "The current operating status of the company",
            "fill_rate": 100.00,
        },
        "company_type": {
            "type": "text",
            "description": "The type of company (eg, private, public)",
            "fill_rate": 96.41,
        },
        "ipo_status": {
            "type": "text",
            "description": "Status of the company regarding Initial Public Offering (IPO)",
            "fill_rate": 99.94,
        },
        "investor_type": {
            "type": "text",
            "description": "Type of investor",
            "fill_rate": 0.00,
        },
        # Location
        "region": {
            "type": "text",
            "description": "The continent where the company's headquarters is located",
            "fill_rate": 93.28,
        },
        "country_code": {
            "type": "text",
            "description": "The country code where the company is located",
            "fill_rate": 93.50,
        },
        "hq_continent": {
            "type": "text",
            "description": "The continent where the company's headquarters is located",
            "fill_rate": 92.59,
        },
        "address": {
            "type": "text",
            "description": "Physical address of the company",
            "fill_rate": 93.50,
        },
        "location": {
            "type": "array",
            "description": "Location information for the company",
            "fill_rate": 93.50,
            "nested_fields": 2,
        },
        "headquarters_regions": {
            "type": "array",
            "description": "Regions where the company has headquarters",
            "fill_rate": 91.62,
            "nested_fields": 2,
        },
        # Industries & products
        "industries": {
            "type": "array",
            "description": "Industries associated with the company",
            "fill_rate": 94.51,
            "nested_fields": 2,
        },
        "total_active_products": {
            "type": "number",
            "description": "Total number of active products",
            "fill_rate": 14.54,
        },
        "siftery_products": {
            "type": "array",
            "description": "Products listed by Siftery",
            "fill_rate": 14.45,
            "nested_fields": 3,
        },
        # Employees & contacts
        "num_employees": {
            "type": "text",
            "description": "The number of employees in the company",
            "fill_rate": 86.28,
        },
        "num_employee_profiles": {
            "type": "number",
            "description": "Number of employee profiles associated with the company",
            "fill_rate": 99.94,
        },
        "number_of_employee_profiles": {
            "type": "number",
            "description": "Number of employee profiles associated with the company",
            "fill_rate": 99.07,
        },
        "num_contacts": {
            "type": "number",
            "description": "Total number of contacts associated with the company",
            "fill_rate": 34.63,
        },
        "number_of_contacts": {
            "type": "number",
            "description": "Total number of contacts associated with the company",
            "fill_rate": 34.10,
        },
        "num_contacts_linkedin": {
            "type": "number",
            "description": "Number of LinkedIn contacts",
            "fill_rate": 34.64,
        },
        "number_of_linkedin_contacts": {
            "type": "number",
            "description": "Number of LinkedIn contacts",
            "fill_rate": 34.10,
        },
        "contacts": {
            "type": "array",
            "description": "Contact information for the company",
            "fill_rate": 46.38,
            "nested_fields": 5,
        },
        "current_employees": {
            "type": "array",
            "description": "Number of current employees",
            "fill_rate": 25.29,
            "nested_fields": 4,
        },
        "num_alumni": {
            "type": "number",
            "description": "Total number of company alumni",
            "fill_rate": 0.02,
        },
        "alumni": {
            "type": "array",
            "description": "Information about company alumni",
            "fill_rate": 0.61,
            "nested_fields": 4,
        },
        # Contact info
        "website": {
            "type": "text",
            "description": "The official website of the company",
            "fill_rate": 97.36,
        },
        "contact_email": {
            "type": "text",
            "description": "Contact email address for the company",
            "fill_rate": 74.28,
        },
        "email_address": {
            "type": "text",
            "description": "Contact email address for the company",
            "fill_rate": 73.56,
        },
        "contact_phone": {
            "type": "text",
            "description": "Contact phone number for the company",
            "fill_rate": 77.90,
        },
        "phone_number": {
            "type": "text",
            "description": "Contact phone number for the company",
            "fill_rate": 77.25,
        },
        "social_media_links": {
            "type": "array",
            "description": "URLs of social media profiles associated with the company",
            "fill_rate": 86.85,
        },
        "socila_media_urls": {
            "type": "array",
            "description": "URLs of social media profiles associated with the company",
            "fill_rate": 85.95,
        },
        # Founding & dates
        "founded_date": {
            "type": "text",
            "description": "The date when the company was founded",
            "fill_rate": 2.42,
        },
        # Funding & investments
        "num_investors": {
            "type": "number",
            "description": "Number of investors in the company",
            "fill_rate": 8.24,
        },
        "investors": {
            "type": "array",
            "description": "List of investors in the company",
            "fill_rate": 8.24,
            "nested_fields": 6,
        },
        "num_investments": {
            "type": "number",
            "description": "Total number of investments made by the company",
            "fill_rate": 2.61,
        },
        "investments": {
            "type": "array",
            "description": "Information about company investments",
            "fill_rate": 2.61,
            "nested_fields": 7,
        },
        "num_investments_lead": {
            "type": "number",
            "description": "Number of investments led by the company",
            "fill_rate": 1.40,
        },
        "funding_rounds_list": {
            "type": "array",
            "description": "List of funding rounds",
            "fill_rate": 10.06,
            "nested_fields": 8,
        },
        "funds_raised": {
            "type": "array",
            "description": "Total funds raised by the company",
            "fill_rate": 2.61,
            "nested_fields": 5,
        },
        "num_funds": {
            "type": "number",
            "description": "Total number of funds",
            "fill_rate": 0.31,
        },
        "funds_list": {
            "type": "array",
            "description": "List of funds associated with the company",
            "fill_rate": 0.31,
            "nested_fields": 3,
        },
        "num_diversity_spotlight_investments": {
            "type": "number",
            "description": "Number of diversity spotlight investments",
            "fill_rate": 0.47,
        },
        "diversity_investments": {
            "type": "array",
            "description": "Information about diversity investments",
            "fill_rate": 0.47,
            "nested_fields": 7,
        },
        # Acquisitions & exits
        "num_acquisitions": {
            "type": "number",
            "description": "Total number of acquisitions by the company",
            "fill_rate": 1.88,
        },
        "acquisitions": {
            "type": "array",
            "description": "Information about company acquisitions",
            "fill_rate": 1.88,
            "nested_fields": 4,
        },
        "acquired_by": {
            "type": "object",
            "description": "Information about the acquiring entity",
            "fill_rate": 4.57,
            "nested_fields": 5,
        },
        "num_exits": {
            "type": "number",
            "description": "Information about company exits",
            "fill_rate": 0.06,
        },
        "exits": {
            "type": "array",
            "description": "Information about company exits",
            "fill_rate": 0.94,
            "nested_fields": 4,
        },
        # Organization structure
        "num_sub_organizations": {
            "type": "number",
            "description": "Total number of sub-organizations",
            "fill_rate": 0.53,
        },
        "sub_organizations": {
            "type": "array",
            "description": "Sub-organizations associated with the company",
            "fill_rate": 0.53,
            "nested_fields": 4,
        },
        "sub_organization_of": {
            "type": "text",
            "description": "Information about being a sub-organization of another entity",
            "fill_rate": 0.80,
        },
        # People
        "founders": {
            "type": "array",
            "description": "Information about the founders of the company",
            "fill_rate": 21.93,
            "nested_fields": 3,
        },
        "num_founder_alumni": {
            "type": "number",
            "description": "Total number of founder alumni",
            "fill_rate": 0.01,
        },
        "num_advisor_positions": {
            "type": "number",
            "description": "Number of advisory positions associated with the company",
            "fill_rate": 3.51,
        },
        "current_advisors": {
            "type": "array",
            "description": "List of current advisors for the company",
            "fill_rate": 3.51,
            "nested_fields": 4,
        },
        "leadership_hire": {
            "type": "array",
            "description": "Leadership hiring information",
            "fill_rate": 1.61,
            "nested_fields": 4,
        },
        "layoff": {
            "type": "array",
            "description": "Layoff information",
            "fill_rate": 0.28,
            "nested_fields": 4,
        },
        "people_highlights": {
            "type": "object",
            "description": "Highlights of people associated with the company",
            "fill_rate": 47.68,
            "nested_fields": 3,
        },
        # Technology
        "active_tech_count": {
            "type": "number",
            "description": "Number of active technologies used by the company",
            "fill_rate": 95.47,
        },
        "builtwith_num_technologies_used": {
            "type": "number",
            "description": "Number of technologies the company is built with",
            "fill_rate": 95.47,
        },
        "built_with_num_technologies_used": {
            "type": "number",
            "description": "Number of technologies the company is built with",
            "fill_rate": 94.61,
        },
        "builtwith_tech": {
            "type": "array",
            "description": "Technologies used by the company",
            "fill_rate": 93.77,
            "nested_fields": 3,
        },
        "built_with_tech": {
            "type": "array",
            "description": "Technologies used by the company",
            "fill_rate": 92.91,
            "nested_fields": 3,
        },
        "technology_highlights": {
            "type": "object",
            "description": "Highlights of technologies used by the company",
            "fill_rate": 96.06,
            "nested_fields": 4,
        },
        # Traffic & analytics
        "monthly_visits": {
            "type": "number",
            "description": "Number of monthly website visits",
            "fill_rate": 52.61,
        },
        "monthly_visits_growth": {
            "type": "number",
            "description": "Growth in monthly visits",
            "fill_rate": 44.34,
        },
        "semrush_visits_latest_month": {
            "type": "number",
            "description": "Latest monthly visits data from SEMrush",
            "fill_rate": 52.61,
        },
        "semrush_visits_mom_pct": {
            "type": "number",
            "description": "Percentage growth in SEMrush visits",
            "fill_rate": 44.34,
        },
        "semrush_last_updated": {
            "type": "text",
            "description": "Last update date for SEMrush data",
            "fill_rate": 52.61,
        },
        "semrush_location_list": {
            "type": "array",
            "description": "List of locations according to SEMrush",
            "fill_rate": 1.78,
            "nested_fields": 5,
        },
        # Third-party data
        "bombora": {
            "type": "array",
            "description": "Bombora information",
            "fill_rate": 21.27,
            "nested_fields": 5,
        },
        "bombora_last_updated": {
            "type": "text",
            "description": "Last update date for Bombora data",
            "fill_rate": 24.26,
        },
        "apptopia": {
            "type": "array",
            "description": "Apptopia data",
            "fill_rate": 5.56,
            "nested_fields": 4,
        },
        "apptopia_total_downloads": {
            "type": "number",
            "description": "Total downloads according to Apptopia",
            "fill_rate": 1.56,
        },
        "apptopia_total_downloads_mom_pct": {
            "type": "text",
            "description": "Month-over-month percentage change in downloads",
            "fill_rate": 1.35,
        },
        "aberdeen_it_spend": {
            "type": "object",
            "description": "IT spending data from Aberdeen",
            "fill_rate": 56.04,
            "nested_fields": 3,
        },
        "ipqwery": {
            "type": "object",
            "description": "IPQwery data",
            "fill_rate": 8.42,
            "nested_fields": 4,
        },
        # Events & news
        "num_event_appearances": {
            "type": "number",
            "description": "Number of appearances in events",
            "fill_rate": 0.10,
        },
        "event_appearances": {
            "type": "array",
            "description": "Number of times the company has appeared in events",
            "fill_rate": 0.10,
            "nested_fields": 5,
        },
        "num_news": {
            "type": "number",
            "description": "Number of news articles related to the company",
            "fill_rate": 0.53,
        },
        "news": {
            "type": "array",
            "description": "News related to the company",
            "fill_rate": 27.91,
            "nested_fields": 6,
        },
        # Lists & features
        "featured_list": {
            "type": "array",
            "description": "Indicates if the company is featured on a list",
            "fill_rate": 95.71,
            "nested_fields": 4,
        },
        "similar_companies": {
            "type": "array",
            "description": "List of companies similar to the specified company",
            "fill_rate": 57.21,
            "nested_fields": 2,
        },
        # Financial highlights
        "financials_highlights": {
            "type": "object",
            "description": "Highlights of financial data",
            "fill_rate": 10.87,
            "nested_fields": 4,
        },
        "ipo_fields": {
            "type": "object",
            "description": "Information related to Initial Public Offering (IPO)",
            "fill_rate": 1.49,
            "nested_fields": 5,
        },
        "stock_symbol": {
            "type": "text",
            "description": "Stock symbol associated with the company",
            "fill_rate": 0.42,
        },
    }

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)

    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names."""
        return list(cls.FIELDS.keys())

    @classmethod
    def get_high_fill_rate_fields(cls, min_rate: float = 50.0) -> list:
        """Get fields with fill rate above threshold."""
        return [name for name, info in cls.FIELDS.items() if info.get("fill_rate", 0) >= min_rate]

    @classmethod
    def get_fields_by_type(cls, field_type: str) -> list:
        """Get fields of a specific type (text, number, array, object, url)."""
        return [name for name, info in cls.FIELDS.items() if info.get("type") == field_type]
