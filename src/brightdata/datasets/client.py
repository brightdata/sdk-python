"""
Datasets client - main entry point for datasets API.

Uses a registry + __getattr__ for lazy-loading dataset instances.
IDE autocomplete is provided via the companion client.pyi stub file.
"""

import importlib
from typing import List, TYPE_CHECKING

from .models import DatasetInfo

if TYPE_CHECKING:
    from ..core.engine import AsyncEngine

# Registry: property_name -> (relative_module, class_name)
# To add a new dataset, just add one line here.
_DATASET_REGISTRY = {
    # LinkedIn
    "linkedin_profiles": (".linkedin", "LinkedInPeopleProfiles"),
    "linkedin_companies": (".linkedin", "LinkedInCompanyProfiles"),
    "linkedin_job_listings": (".linkedin", "LinkedInJobListings"),
    "linkedin_posts": (".linkedin", "LinkedInPosts"),
    "linkedin_profiles_job_listings": (".linkedin", "LinkedInProfilesJobListings"),
    # Amazon
    "amazon_products": (".amazon", "AmazonProducts"),
    "amazon_reviews": (".amazon", "AmazonReviews"),
    "amazon_sellers_info": (".amazon", "AmazonSellersInfo"),
    "amazon_best_sellers": (".amazon", "AmazonBestSellers"),
    "amazon_products_search": (".amazon", "AmazonProductsSearch"),
    "amazon_products_global": (".amazon", "AmazonProductsGlobal"),
    "amazon_walmart": (".amazon", "AmazonWalmart"),
    # Business Data
    "crunchbase_companies": (".crunchbase", "CrunchbaseCompanies"),
    "zoominfo_companies": (".zoominfo", "ZoomInfoCompanies"),
    "pitchbook_companies": (".pitchbook", "PitchBookCompanies"),
    "slintel_companies": (".slintel", "SlintelCompanies"),
    "owler_companies": (".owler", "OwlerCompanies"),
    "ventureradar_companies": (".ventureradar", "VentureRadarCompanies"),
    "companies_enriched": (".companies_enriched", "CompaniesEnriched"),
    "employees_enriched": (".employees_enriched", "EmployeesEnriched"),
    "manta_businesses": (".manta", "MantaBusinesses"),
    # Reviews & Ratings
    "glassdoor_companies": (".glassdoor", "GlassdoorCompanies"),
    "glassdoor_reviews": (".glassdoor", "GlassdoorReviews"),
    "glassdoor_jobs": (".glassdoor", "GlassdoorJobs"),
    "google_maps_reviews": (".google_maps", "GoogleMapsReviews"),
    "google_maps_full_info": (".google_maps", "GoogleMapsFullInfo"),
    "yelp_businesses": (".yelp", "YelpBusinesses"),
    "yelp_reviews": (".yelp", "YelpReviews"),
    "g2_products": (".g2", "G2Products"),
    "g2_reviews": (".g2", "G2Reviews"),
    "trustpilot_reviews": (".trustpilot", "TrustpilotReviews"),
    "trustradius_reviews": (".trustradius", "TrustRadiusReviews"),
    # Jobs
    "indeed_companies": (".indeed", "IndeedCompanies"),
    "indeed_jobs": (".indeed", "IndeedJobs"),
    "xing_profiles": (".xing", "XingProfiles"),
    "us_lawyers": (".lawyers", "USLawyers"),
    # Social Media - Instagram
    "instagram_profiles": (".instagram", "InstagramProfiles"),
    "instagram_posts": (".instagram", "InstagramPosts"),
    "instagram_comments": (".instagram", "InstagramComments"),
    "instagram_reels": (".instagram", "InstagramReels"),
    # Social Media - TikTok
    "tiktok_profiles": (".tiktok", "TikTokProfiles"),
    "tiktok_posts": (".tiktok", "TikTokPosts"),
    "tiktok_comments": (".tiktok", "TikTokComments"),
    "tiktok_shop": (".tiktok", "TikTokShop"),
    # Social Media - Facebook
    "facebook_pages_posts": (".facebook", "FacebookPagesPosts"),
    "facebook_comments": (".facebook", "FacebookComments"),
    "facebook_posts_by_url": (".facebook", "FacebookPostsByUrl"),
    "facebook_reels": (".facebook", "FacebookReels"),
    "facebook_marketplace": (".facebook", "FacebookMarketplace"),
    "facebook_company_reviews": (".facebook", "FacebookCompanyReviews"),
    "facebook_events": (".facebook", "FacebookEvents"),
    "facebook_profiles": (".facebook", "FacebookProfiles"),
    "facebook_pages_profiles": (".facebook", "FacebookPagesProfiles"),
    "facebook_group_posts": (".facebook", "FacebookGroupPosts"),
    # Social Media - X/Twitter
    "x_twitter_posts": (".x_twitter", "XTwitterPosts"),
    "x_twitter_profiles": (".x_twitter", "XTwitterProfiles"),
    # Social Media - Other
    "reddit_posts": (".reddit", "RedditPosts"),
    "reddit_comments": (".reddit", "RedditComments"),
    "bluesky_posts": (".bluesky", "BlueskyPosts"),
    "bluesky_top_profiles": (".bluesky", "BlueskyTopProfiles"),
    "snapchat_posts": (".snapchat", "SnapchatPosts"),
    "quora_posts": (".quora", "QuoraPosts"),
    "pinterest_posts": (".pinterest", "PinterestPosts"),
    "pinterest_profiles": (".pinterest", "PinterestProfiles"),
    # Video
    "youtube_profiles": (".youtube", "YouTubeProfiles"),
    "youtube_videos": (".youtube", "YouTubeVideos"),
    "youtube_comments": (".youtube", "YouTubeComments"),
    "vimeo_videos": (".vimeo", "VimeoVideos"),
    # News & Content
    "google_news": (".google_news", "GoogleNews"),
    "wikipedia_articles": (".wikipedia", "WikipediaArticles"),
    "bbc_news": (".bbc", "BBCNews"),
    "cnn_news": (".cnn", "CNNNews"),
    "github_repositories": (".github", "GithubRepositories"),
    "creative_commons_images": (".creative_commons", "CreativeCommonsImages"),
    "creative_commons_3d_models": (".creative_commons", "CreativeCommons3DModels"),
    # App Stores
    "google_play_store": (".google_play", "GooglePlayStore"),
    "google_play_reviews": (".google_play", "GooglePlayReviews"),
    "apple_app_store": (".apple_appstore", "AppleAppStore"),
    "apple_app_store_reviews": (".apple_appstore", "AppleAppStoreReviews"),
    # E-commerce - General
    "walmart_products": (".walmart", "WalmartProducts"),
    "walmart_sellers_info": (".walmart", "WalmartSellersInfo"),
    "ebay_products": (".ebay", "EbayProducts"),
    "etsy_products": (".etsy", "EtsyProducts"),
    "target_products": (".target", "TargetProducts"),
    "bestbuy_products": (".bestbuy", "BestBuyProducts"),
    "costco_products": (".costco", "CostcoProducts"),
    "macys_products": (".macys", "MacysProducts"),
    "kroger_products": (".kroger", "KrogerProducts"),
    "wayfair_products": (".wayfair", "WayfairProducts"),
    "shein_products": (".shein", "SheinProducts"),
    # E-commerce - Electronics
    "digikey_products": (".digikey", "DigikeyProducts"),
    "mouser_products": (".mouser", "MouserProducts"),
    "microcenter_products": (".microcenter", "MicroCenterProducts"),
    "autozone_products": (".autozone", "AutozoneProducts"),
    "bh_products": (".bh", "BHProducts"),
    "mediamarkt_products": (".mediamarkt", "MediamarktProducts"),
    # E-commerce - Fashion
    "zalando_products": (".zalando", "ZalandoProducts"),
    "sephora_products": (".sephora", "SephoraProducts"),
    "zara_products": (".zara", "ZaraProducts"),
    "zara_home_products": (".zara", "ZaraHomeProducts"),
    "mango_products": (".mango", "MangoProducts"),
    "massimo_dutti_products": (".massimo_dutti", "MassimoDuttiProducts"),
    "asos_products": (".asos", "AsosProducts"),
    "hm_products": (".hm", "HMProducts"),
    "american_eagle_products": (".american_eagle", "AmericanEagleProducts"),
    "myntra_products": (".myntra", "MyntraProducts"),
    # E-commerce - Luxury
    "chanel_products": (".chanel", "ChanelProducts"),
    "dior_products": (".dior", "DiorProducts"),
    "fendi_products": (".fendi", "FendiProducts"),
    "balenciaga_products": (".balenciaga", "BalenciagaProducts"),
    "bottegaveneta_products": (".bottegaveneta", "BottegaVenetaProducts"),
    "celine_products": (".celine", "CelineProducts"),
    "loewe_products": (".loewe", "LoeweProducts"),
    "berluti_products": (".berluti", "BerlutiProducts"),
    "moynat_products": (".moynat", "MoynatProducts"),
    "hermes_products": (".hermes", "HermesProducts"),
    "delvaux_products": (".delvaux", "DelvauxProducts"),
    "prada_products": (".prada", "PradaProducts"),
    "montblanc_products": (".montblanc", "MontblancProducts"),
    "ysl_products": (".ysl", "YSLProducts"),
    # E-commerce - Home & Furniture
    "ikea_products": (".ikea", "IkeaProducts"),
    "ashley_furniture_products": (".ashley_furniture", "AshleyFurnitureProducts"),
    "crateandbarrel_products": (".crateandbarrel", "CrateAndBarrelProducts"),
    "lazboy_products": (".lazboy", "LaZBoyProducts"),
    "mattressfirm_products": (".mattressfirm", "MattressfirmProducts"),
    "sleepnumber_products": (".sleepnumber", "SleepNumberProducts"),
    "raymourflanigan_products": (".raymourflanigan", "RaymourFlaniganProducts"),
    "mybobs_products": (".mybobs", "MybobsProducts"),
    # E-commerce - Other
    "fanatics_products": (".fanatics", "FanaticsProducts"),
    "carters_products": (".carters", "CartersProducts"),
    "lego_products": (".lego", "LegoProducts"),
    "llbean_products": (".llbean", "LLBeanProducts"),
    "toysrus_products": (".toysrus", "ToysRUsProducts"),
    "homedepot_us_products": (".homedepot", "HomeDepotUSProducts"),
    "homedepot_ca_products": (".homedepot", "HomeDepotCAProducts"),
    "lowes_products": (".lowes", "LowesProducts"),
    "rona_products": (".rona", "RonaProducts"),
    # E-commerce - International
    "shopee_products": (".shopee", "ShopeeProducts"),
    "lazada_products": (".lazada", "LazadaProducts"),
    "lazada_reviews": (".lazada", "LazadaReviews"),
    "lazada_products_search": (".lazada", "LazadaProductsSearch"),
    "ozon_products": (".ozon", "OzonProducts"),
    "wildberries_products": (".wildberries", "WildberriesProducts"),
    "tokopedia_products": (".tokopedia", "TokopediaProducts"),
    "mercadolivre_products": (".mercadolivre", "MercadolivreProducts"),
    "naver_products": (".naver", "NaverProducts"),
    "google_shopping_products": (".google_shopping", "GoogleShoppingProducts"),
    "google_shopping_search_us": (".google_shopping", "GoogleShoppingSearchUS"),
    # Real Estate
    "australia_real_estate": (".real_estate", "AustraliaRealEstate"),
    "zillow_properties": (".zillow", "ZillowProperties"),
    "zillow_price_history": (".zillow", "ZillowPriceHistory"),
    "zoopla_properties": (".zoopla", "ZooplaProperties"),
    "otodom_poland": (".otodom", "OtodomPoland"),
    "inmuebles24_mexico": (".inmuebles24", "Inmuebles24Mexico"),
    "zonaprop_argentina": (".zonaprop", "ZonapropArgentina"),
    "metrocuadrado_properties": (".metrocuadrado", "MetrocuadradoProperties"),
    "infocasas_uruguay": (".infocasas", "InfocasasUruguay"),
    "properati_properties": (".properati", "ProperatiProperties"),
    "toctoc_properties": (".toctoc", "ToctocProperties"),
    "realtor_international_properties": (".realtor", "RealtorInternationalProperties"),
    # Travel
    "airbnb_properties": (".airbnb", "AirbnbProperties"),
    "booking_listings_search": (".booking", "BookingListingsSearch"),
    "booking_hotel_listings": (".booking", "BookingHotelListings"),
    "agoda_properties": (".agoda", "AgodaProperties"),
    # Automotive
    "webmotors_brasil": (".webmotors", "WebmotorsBrasil"),
    "chileautos_chile": (".chileautos", "ChileautosChile"),
    "carsales_listings": (".carsales", "CarsalesListings"),
    # Classifieds
    "olx_brazil": (".olx", "OLXBrazil"),
    "yapo_chile": (".yapo", "YapoChile"),
    # Reference Data
    "imdb_movies": (".imdb", "IMDBMovies"),
    "nba_players_stats": (".nba", "NBAPlayersStats"),
    "goodreads_books": (".goodreads", "GoodreadsBooks"),
    "world_population": (".world_population", "WorldPopulation"),
    "world_zipcodes": (".world_zipcodes", "WorldZipcodes"),
    # Finance
    "yahoo_finance_businesses": (".yahoo_finance", "YahooFinanceBusinesses"),
}


class DatasetsClient:
    """
    Client for Bright Data Datasets API.

    Access pre-collected datasets and filter records.

    Usage:
        async with BrightDataClient() as client:
            # List all datasets
            datasets = await client.datasets.list()

            # Get metadata for a specific dataset
            metadata = await client.datasets.linkedin_profiles.get_metadata()

            # Filter records
            snapshot_id = await client.datasets.linkedin_profiles.filter(
                filter={"name": "industry", "operator": "=", "value": "Technology"},
                records_limit=100
            )

            # Download results
            data = await client.datasets.linkedin_profiles.download(snapshot_id)
    """

    BASE_URL = "https://api.brightdata.com"

    def __init__(self, engine: "AsyncEngine"):
        self._engine = engine
        self._cache: dict = {}

    def __getattr__(self, name: str):
        if name in _DATASET_REGISTRY:
            if name not in self._cache:
                module_path, class_name = _DATASET_REGISTRY[name]
                module = importlib.import_module(module_path, package=__package__)
                cls = getattr(module, class_name)
                self._cache[name] = cls(self._engine)
            return self._cache[name]
        raise AttributeError(
            f"'{type(self).__name__}' has no dataset '{name}'. "
            f"Available datasets: {', '.join(sorted(_DATASET_REGISTRY))}"
        )

    async def list(self) -> List[DatasetInfo]:
        """
        List all available datasets.

        Returns:
            List of DatasetInfo with id, name, and size
        """
        async with self._engine.get_from_url(f"{self.BASE_URL}/datasets/list") as response:
            data = await response.json()

        datasets = []
        for item in data:
            datasets.append(
                DatasetInfo(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    size=item.get("size", 0),
                )
            )
        return datasets
