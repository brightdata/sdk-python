"""
Datasets client - main entry point for datasets API.
"""

from typing import List, Optional, TYPE_CHECKING

from .models import DatasetInfo
from .linkedin import (
    LinkedInPeopleProfiles,
    LinkedInCompanyProfiles,
    LinkedInJobListings,
    LinkedInPosts,
    LinkedInProfilesJobListings,
)
from .amazon import (
    AmazonProducts,
    AmazonReviews,
    AmazonSellersInfo,
    AmazonBestSellers,
    AmazonProductsSearch,
    AmazonProductsGlobal,
    AmazonWalmart,
)
from .crunchbase import CrunchbaseCompanies
from .imdb import IMDBMovies
from .nba import NBAPlayersStats
from .goodreads import GoodreadsBooks
from .world_population import WorldPopulation
from .companies_enriched import CompaniesEnriched
from .employees_enriched import EmployeesEnriched
from .glassdoor import GlassdoorCompanies, GlassdoorReviews, GlassdoorJobs
from .google_maps import GoogleMapsReviews, GoogleMapsFullInfo
from .yelp import YelpBusinesses, YelpReviews
from .zoominfo import ZoomInfoCompanies
from .pitchbook import PitchBookCompanies
from .g2 import G2Products, G2Reviews
from .trustpilot import TrustpilotReviews
from .indeed import IndeedCompanies, IndeedJobs
from .xing import XingProfiles
from .slintel import SlintelCompanies
from .owler import OwlerCompanies
from .lawyers import USLawyers
from .manta import MantaBusinesses
from .ventureradar import VentureRadarCompanies
from .trustradius import TrustRadiusReviews
from .instagram import InstagramProfiles, InstagramPosts, InstagramComments, InstagramReels
from .tiktok import TikTokProfiles, TikTokComments, TikTokPosts, TikTokShop
from .real_estate import AustraliaRealEstate
from .walmart import WalmartProducts, WalmartSellersInfo
from .mediamarkt import MediamarktProducts
from .fendi import FendiProducts
from .zalando import ZalandoProducts
from .sephora import SephoraProducts
from .zara import ZaraProducts, ZaraHomeProducts
from .mango import MangoProducts
from .massimo_dutti import MassimoDuttiProducts
from .otodom import OtodomPoland
from .webmotors import WebmotorsBrasil
from .airbnb import AirbnbProperties
from .asos import AsosProducts
from .chanel import ChanelProducts
from .ashley_furniture import AshleyFurnitureProducts
from .fanatics import FanaticsProducts
from .carters import CartersProducts
from .american_eagle import AmericanEagleProducts
from .ikea import IkeaProducts
from .hm import HMProducts
from .lego import LegoProducts
from .mattressfirm import MattressfirmProducts
from .crateandbarrel import CrateAndBarrelProducts
from .llbean import LLBeanProducts
from .shein import SheinProducts
from .toysrus import ToysRUsProducts
from .mybobs import MybobsProducts
from .sleepnumber import SleepNumberProducts
from .raymourflanigan import RaymourFlaniganProducts
from .inmuebles24 import Inmuebles24Mexico
from .mouser import MouserProducts
from .zillow import ZillowProperties, ZillowPriceHistory
from .zonaprop import ZonapropArgentina
from .metrocuadrado import MetrocuadradoProperties
from .chileautos import ChileautosChile
from .infocasas import InfocasasUruguay
from .lazboy import LaZBoyProducts
from .properati import ProperatiProperties
from .yapo import YapoChile
from .toctoc import ToctocProperties
from .dior import DiorProducts
from .balenciaga import BalenciagaProducts
from .bottegaveneta import BottegaVenetaProducts
from .olx import OLXBrazil
from .celine import CelineProducts
from .loewe import LoeweProducts
from .berluti import BerlutiProducts
from .moynat import MoynatProducts
from .hermes import HermesProducts
from .delvaux import DelvauxProducts
from .prada import PradaProducts
from .montblanc import MontblancProducts
from .ysl import YSLProducts
from .world_zipcodes import WorldZipcodes
from .pinterest import PinterestPosts, PinterestProfiles
from .shopee import ShopeeProducts
from .lazada import LazadaProducts, LazadaReviews, LazadaProductsSearch
from .youtube import YouTubeProfiles, YouTubeVideos, YouTubeComments
from .digikey import DigikeyProducts
from .facebook import (
    FacebookPagesPosts,
    FacebookComments,
    FacebookPostsByUrl,
    FacebookReels,
    FacebookMarketplace,
    FacebookCompanyReviews,
    FacebookEvents,
    FacebookProfiles,
    FacebookPagesProfiles,
    FacebookGroupPosts,
)
from .x_twitter import XTwitterPosts, XTwitterProfiles
from .reddit import RedditPosts, RedditComments
from .bluesky import BlueskyPosts, BlueskyTopProfiles
from .snapchat import SnapchatPosts
from .quora import QuoraPosts
from .vimeo import VimeoVideos
from .google_news import GoogleNews
from .wikipedia import WikipediaArticles
from .bbc import BBCNews
from .cnn import CNNNews
from .github import GithubRepositories
from .creative_commons import CreativeCommonsImages, CreativeCommons3DModels
from .google_play import GooglePlayStore, GooglePlayReviews
from .apple_appstore import AppleAppStore, AppleAppStoreReviews
from .ebay import EbayProducts
from .etsy import EtsyProducts
from .target import TargetProducts
from .wayfair import WayfairProducts
from .bestbuy import BestBuyProducts
from .myntra import MyntraProducts
from .ozon import OzonProducts
from .wildberries import WildberriesProducts
from .tokopedia import TokopediaProducts
from .google_shopping import GoogleShoppingProducts, GoogleShoppingSearchUS
from .mercadolivre import MercadolivreProducts
from .naver import NaverProducts
from .homedepot import HomeDepotUSProducts, HomeDepotCAProducts
from .lowes import LowesProducts
from .rona import RonaProducts
from .kroger import KrogerProducts
from .macys import MacysProducts
from .costco import CostcoProducts
from .bh import BHProducts
from .microcenter import MicroCenterProducts
from .autozone import AutozoneProducts
from .zoopla import ZooplaProperties
from .booking import BookingListingsSearch, BookingHotelListings
from .realtor import RealtorInternationalProperties
from .agoda import AgodaProperties
from .carsales import CarsalesListings
from .yahoo_finance import YahooFinanceBusinesses

if TYPE_CHECKING:
    from ..core.async_engine import AsyncEngine


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

        # Lazy-loaded dataset instances
        self._linkedin_profiles: Optional[LinkedInPeopleProfiles] = None
        self._linkedin_companies: Optional[LinkedInCompanyProfiles] = None
        self._linkedin_job_listings: Optional[LinkedInJobListings] = None
        self._amazon_products: Optional[AmazonProducts] = None
        self._amazon_reviews: Optional[AmazonReviews] = None
        self._crunchbase_companies: Optional[CrunchbaseCompanies] = None
        self._imdb_movies: Optional[IMDBMovies] = None
        self._nba_players_stats: Optional[NBAPlayersStats] = None
        self._goodreads_books: Optional[GoodreadsBooks] = None
        self._world_population: Optional[WorldPopulation] = None
        self._companies_enriched: Optional[CompaniesEnriched] = None
        self._employees_enriched: Optional[EmployeesEnriched] = None
        self._glassdoor_companies: Optional[GlassdoorCompanies] = None
        self._glassdoor_reviews: Optional[GlassdoorReviews] = None
        self._glassdoor_jobs: Optional[GlassdoorJobs] = None
        self._google_maps_reviews: Optional[GoogleMapsReviews] = None
        self._yelp_businesses: Optional[YelpBusinesses] = None
        self._yelp_reviews: Optional[YelpReviews] = None
        self._zoominfo_companies: Optional[ZoomInfoCompanies] = None
        self._pitchbook_companies: Optional[PitchBookCompanies] = None
        self._g2_products: Optional[G2Products] = None
        self._g2_reviews: Optional[G2Reviews] = None
        self._trustpilot_reviews: Optional[TrustpilotReviews] = None
        self._indeed_companies: Optional[IndeedCompanies] = None
        self._xing_profiles: Optional[XingProfiles] = None
        self._slintel_companies: Optional[SlintelCompanies] = None
        self._owler_companies: Optional[OwlerCompanies] = None
        self._us_lawyers: Optional[USLawyers] = None
        self._manta_businesses: Optional[MantaBusinesses] = None
        self._ventureradar_companies: Optional[VentureRadarCompanies] = None
        self._trustradius_reviews: Optional[TrustRadiusReviews] = None
        self._instagram_profiles: Optional[InstagramProfiles] = None
        self._tiktok_profiles: Optional[TikTokProfiles] = None
        self._australia_real_estate: Optional[AustraliaRealEstate] = None
        self._indeed_jobs: Optional[IndeedJobs] = None
        self._walmart_products: Optional[WalmartProducts] = None
        self._mediamarkt_products: Optional[MediamarktProducts] = None
        self._fendi_products: Optional[FendiProducts] = None
        self._zalando_products: Optional[ZalandoProducts] = None
        self._sephora_products: Optional[SephoraProducts] = None
        self._zara_products: Optional[ZaraProducts] = None
        self._zara_home_products: Optional[ZaraHomeProducts] = None
        self._mango_products: Optional[MangoProducts] = None
        self._massimo_dutti_products: Optional[MassimoDuttiProducts] = None
        self._otodom_poland: Optional[OtodomPoland] = None
        self._webmotors_brasil: Optional[WebmotorsBrasil] = None
        self._airbnb_properties: Optional[AirbnbProperties] = None
        self._asos_products: Optional[AsosProducts] = None
        self._chanel_products: Optional[ChanelProducts] = None
        self._ashley_furniture_products: Optional[AshleyFurnitureProducts] = None
        self._fanatics_products: Optional[FanaticsProducts] = None
        self._carters_products: Optional[CartersProducts] = None
        self._american_eagle_products: Optional[AmericanEagleProducts] = None
        self._ikea_products: Optional[IkeaProducts] = None
        self._hm_products: Optional[HMProducts] = None
        self._lego_products: Optional[LegoProducts] = None
        self._mattressfirm_products: Optional[MattressfirmProducts] = None
        self._crateandbarrel_products: Optional[CrateAndBarrelProducts] = None
        self._llbean_products: Optional[LLBeanProducts] = None
        self._shein_products: Optional[SheinProducts] = None
        self._toysrus_products: Optional[ToysRUsProducts] = None
        self._mybobs_products: Optional[MybobsProducts] = None
        self._sleepnumber_products: Optional[SleepNumberProducts] = None
        self._raymourflanigan_products: Optional[RaymourFlaniganProducts] = None
        self._inmuebles24_mexico: Optional[Inmuebles24Mexico] = None
        self._mouser_products: Optional[MouserProducts] = None
        self._zillow_properties: Optional[ZillowProperties] = None
        self._zonaprop_argentina: Optional[ZonapropArgentina] = None
        self._metrocuadrado_properties: Optional[MetrocuadradoProperties] = None
        self._chileautos_chile: Optional[ChileautosChile] = None
        self._infocasas_uruguay: Optional[InfocasasUruguay] = None
        self._lazboy_products: Optional[LaZBoyProducts] = None
        self._properati_properties: Optional[ProperatiProperties] = None
        self._yapo_chile: Optional[YapoChile] = None
        self._toctoc_properties: Optional[ToctocProperties] = None
        self._dior_products: Optional[DiorProducts] = None
        self._balenciaga_products: Optional[BalenciagaProducts] = None
        self._bottegaveneta_products: Optional[BottegaVenetaProducts] = None
        self._olx_brazil: Optional[OLXBrazil] = None
        self._celine_products: Optional[CelineProducts] = None
        self._loewe_products: Optional[LoeweProducts] = None
        self._berluti_products: Optional[BerlutiProducts] = None
        self._moynat_products: Optional[MoynatProducts] = None
        self._hermes_products: Optional[HermesProducts] = None
        self._delvaux_products: Optional[DelvauxProducts] = None
        self._prada_products: Optional[PradaProducts] = None
        self._montblanc_products: Optional[MontblancProducts] = None
        self._ysl_products: Optional[YSLProducts] = None
        self._amazon_sellers_info: Optional[AmazonSellersInfo] = None
        self._world_zipcodes: Optional[WorldZipcodes] = None
        self._pinterest_posts: Optional[PinterestPosts] = None
        self._pinterest_profiles: Optional[PinterestProfiles] = None
        self._shopee_products: Optional[ShopeeProducts] = None
        self._lazada_products: Optional[LazadaProducts] = None
        self._instagram_posts: Optional[InstagramPosts] = None
        self._youtube_profiles: Optional[YouTubeProfiles] = None
        self._youtube_videos: Optional[YouTubeVideos] = None
        self._youtube_comments: Optional[YouTubeComments] = None
        self._digikey_products: Optional[DigikeyProducts] = None
        self._facebook_pages_posts: Optional[FacebookPagesPosts] = None
        # New datasets - Social Media
        self._facebook_comments: Optional[FacebookComments] = None
        self._facebook_posts_by_url: Optional[FacebookPostsByUrl] = None
        self._facebook_reels: Optional[FacebookReels] = None
        self._facebook_marketplace: Optional[FacebookMarketplace] = None
        self._facebook_company_reviews: Optional[FacebookCompanyReviews] = None
        self._facebook_events: Optional[FacebookEvents] = None
        self._facebook_profiles: Optional[FacebookProfiles] = None
        self._facebook_pages_profiles: Optional[FacebookPagesProfiles] = None
        self._facebook_group_posts: Optional[FacebookGroupPosts] = None
        self._tiktok_comments: Optional[TikTokComments] = None
        self._tiktok_posts: Optional[TikTokPosts] = None
        self._tiktok_shop: Optional[TikTokShop] = None
        self._instagram_comments: Optional[InstagramComments] = None
        self._instagram_reels: Optional[InstagramReels] = None
        self._linkedin_posts: Optional[LinkedInPosts] = None
        self._linkedin_profiles_job_listings: Optional[LinkedInProfilesJobListings] = None
        self._x_twitter_posts: Optional[XTwitterPosts] = None
        self._x_twitter_profiles: Optional[XTwitterProfiles] = None
        self._reddit_posts: Optional[RedditPosts] = None
        self._reddit_comments: Optional[RedditComments] = None
        self._bluesky_posts: Optional[BlueskyPosts] = None
        self._bluesky_top_profiles: Optional[BlueskyTopProfiles] = None
        self._snapchat_posts: Optional[SnapchatPosts] = None
        self._quora_posts: Optional[QuoraPosts] = None
        self._vimeo_videos: Optional[VimeoVideos] = None
        # New datasets - News/Content
        self._google_news: Optional[GoogleNews] = None
        self._wikipedia_articles: Optional[WikipediaArticles] = None
        self._bbc_news: Optional[BBCNews] = None
        self._cnn_news: Optional[CNNNews] = None
        self._github_repositories: Optional[GithubRepositories] = None
        self._creative_commons_images: Optional[CreativeCommonsImages] = None
        self._creative_commons_3d_models: Optional[CreativeCommons3DModels] = None
        # New datasets - App Stores
        self._google_play_store: Optional[GooglePlayStore] = None
        self._google_play_reviews: Optional[GooglePlayReviews] = None
        self._apple_app_store: Optional[AppleAppStore] = None
        self._apple_app_store_reviews: Optional[AppleAppStoreReviews] = None
        # New datasets - E-commerce
        self._amazon_best_sellers: Optional[AmazonBestSellers] = None
        self._amazon_products_search: Optional[AmazonProductsSearch] = None
        self._amazon_products_global: Optional[AmazonProductsGlobal] = None
        self._amazon_walmart: Optional[AmazonWalmart] = None
        self._walmart_sellers_info: Optional[WalmartSellersInfo] = None
        self._ebay_products: Optional[EbayProducts] = None
        self._etsy_products: Optional[EtsyProducts] = None
        self._target_products: Optional[TargetProducts] = None
        self._wayfair_products: Optional[WayfairProducts] = None
        self._bestbuy_products: Optional[BestBuyProducts] = None
        self._myntra_products: Optional[MyntraProducts] = None
        self._ozon_products: Optional[OzonProducts] = None
        self._wildberries_products: Optional[WildberriesProducts] = None
        self._tokopedia_products: Optional[TokopediaProducts] = None
        self._google_shopping_products: Optional[GoogleShoppingProducts] = None
        self._google_shopping_search_us: Optional[GoogleShoppingSearchUS] = None
        self._mercadolivre_products: Optional[MercadolivreProducts] = None
        self._naver_products: Optional[NaverProducts] = None
        self._lazada_reviews: Optional[LazadaReviews] = None
        self._lazada_products_search: Optional[LazadaProductsSearch] = None
        self._homedepot_us_products: Optional[HomeDepotUSProducts] = None
        self._homedepot_ca_products: Optional[HomeDepotCAProducts] = None
        self._lowes_products: Optional[LowesProducts] = None
        self._rona_products: Optional[RonaProducts] = None
        self._kroger_products: Optional[KrogerProducts] = None
        self._macys_products: Optional[MacysProducts] = None
        self._costco_products: Optional[CostcoProducts] = None
        self._bh_products: Optional[BHProducts] = None
        self._microcenter_products: Optional[MicroCenterProducts] = None
        self._autozone_products: Optional[AutozoneProducts] = None
        # New datasets - Real Estate/Travel
        self._zillow_price_history: Optional[ZillowPriceHistory] = None
        self._zoopla_properties: Optional[ZooplaProperties] = None
        self._booking_listings_search: Optional[BookingListingsSearch] = None
        self._booking_hotel_listings: Optional[BookingHotelListings] = None
        self._realtor_international_properties: Optional[RealtorInternationalProperties] = None
        self._agoda_properties: Optional[AgodaProperties] = None
        self._carsales_listings: Optional[CarsalesListings] = None
        # New datasets - Finance/Maps
        self._yahoo_finance_businesses: Optional[YahooFinanceBusinesses] = None
        self._google_maps_full_info: Optional[GoogleMapsFullInfo] = None

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

    # Dataset properties for IDE autocomplete

    @property
    def linkedin_profiles(self) -> LinkedInPeopleProfiles:
        """LinkedIn People Profiles dataset (620M+ records)."""
        if self._linkedin_profiles is None:
            self._linkedin_profiles = LinkedInPeopleProfiles(self._engine)
        return self._linkedin_profiles

    @property
    def linkedin_companies(self) -> LinkedInCompanyProfiles:
        """LinkedIn Company Profiles dataset."""
        if self._linkedin_companies is None:
            self._linkedin_companies = LinkedInCompanyProfiles(self._engine)
        return self._linkedin_companies

    @property
    def linkedin_job_listings(self) -> LinkedInJobListings:
        """LinkedIn Profiles Jobs Listings dataset."""
        if self._linkedin_job_listings is None:
            self._linkedin_job_listings = LinkedInJobListings(self._engine)
        return self._linkedin_job_listings

    @property
    def amazon_products(self) -> AmazonProducts:
        """Amazon Products dataset."""
        if self._amazon_products is None:
            self._amazon_products = AmazonProducts(self._engine)
        return self._amazon_products

    @property
    def amazon_reviews(self) -> AmazonReviews:
        """Amazon Reviews dataset."""
        if self._amazon_reviews is None:
            self._amazon_reviews = AmazonReviews(self._engine)
        return self._amazon_reviews

    @property
    def crunchbase_companies(self) -> CrunchbaseCompanies:
        """Crunchbase Companies dataset (2.3M+ records)."""
        if self._crunchbase_companies is None:
            self._crunchbase_companies = CrunchbaseCompanies(self._engine)
        return self._crunchbase_companies

    @property
    def imdb_movies(self) -> IMDBMovies:
        """IMDB Movies dataset (867K+ records)."""
        if self._imdb_movies is None:
            self._imdb_movies = IMDBMovies(self._engine)
        return self._imdb_movies

    @property
    def nba_players_stats(self) -> NBAPlayersStats:
        """NBA Players Stats dataset (17K+ records)."""
        if self._nba_players_stats is None:
            self._nba_players_stats = NBAPlayersStats(self._engine)
        return self._nba_players_stats

    @property
    def goodreads_books(self) -> GoodreadsBooks:
        """Goodreads Books dataset."""
        if self._goodreads_books is None:
            self._goodreads_books = GoodreadsBooks(self._engine)
        return self._goodreads_books

    @property
    def world_population(self) -> WorldPopulation:
        """World Population dataset."""
        if self._world_population is None:
            self._world_population = WorldPopulation(self._engine)
        return self._world_population

    @property
    def companies_enriched(self) -> CompaniesEnriched:
        """Companies Enriched dataset - multi-source company information."""
        if self._companies_enriched is None:
            self._companies_enriched = CompaniesEnriched(self._engine)
        return self._companies_enriched

    @property
    def employees_enriched(self) -> EmployeesEnriched:
        """Employees Business Enriched dataset - LinkedIn profiles with company data."""
        if self._employees_enriched is None:
            self._employees_enriched = EmployeesEnriched(self._engine)
        return self._employees_enriched

    @property
    def glassdoor_companies(self) -> GlassdoorCompanies:
        """Glassdoor Companies Overview dataset - ratings, reviews, and company details."""
        if self._glassdoor_companies is None:
            self._glassdoor_companies = GlassdoorCompanies(self._engine)
        return self._glassdoor_companies

    @property
    def glassdoor_reviews(self) -> GlassdoorReviews:
        """Glassdoor Companies Reviews dataset - employee reviews and ratings."""
        if self._glassdoor_reviews is None:
            self._glassdoor_reviews = GlassdoorReviews(self._engine)
        return self._glassdoor_reviews

    @property
    def glassdoor_jobs(self) -> GlassdoorJobs:
        """Glassdoor Job Listings dataset - job postings with company data."""
        if self._glassdoor_jobs is None:
            self._glassdoor_jobs = GlassdoorJobs(self._engine)
        return self._glassdoor_jobs

    @property
    def google_maps_reviews(self) -> GoogleMapsReviews:
        """Google Maps Reviews dataset - place reviews and ratings."""
        if self._google_maps_reviews is None:
            self._google_maps_reviews = GoogleMapsReviews(self._engine)
        return self._google_maps_reviews

    @property
    def yelp_businesses(self) -> YelpBusinesses:
        """Yelp Businesses Overview dataset - business listings and ratings."""
        if self._yelp_businesses is None:
            self._yelp_businesses = YelpBusinesses(self._engine)
        return self._yelp_businesses

    @property
    def yelp_reviews(self) -> YelpReviews:
        """Yelp Business Reviews dataset - individual business reviews."""
        if self._yelp_reviews is None:
            self._yelp_reviews = YelpReviews(self._engine)
        return self._yelp_reviews

    @property
    def zoominfo_companies(self) -> ZoomInfoCompanies:
        """ZoomInfo Companies dataset - company data with financials and contacts."""
        if self._zoominfo_companies is None:
            self._zoominfo_companies = ZoomInfoCompanies(self._engine)
        return self._zoominfo_companies

    @property
    def pitchbook_companies(self) -> PitchBookCompanies:
        """PitchBook Companies dataset - PE/VC company data with deals."""
        if self._pitchbook_companies is None:
            self._pitchbook_companies = PitchBookCompanies(self._engine)
        return self._pitchbook_companies

    @property
    def g2_products(self) -> G2Products:
        """G2 Software Product Overview dataset - software ratings and reviews."""
        if self._g2_products is None:
            self._g2_products = G2Products(self._engine)
        return self._g2_products

    @property
    def g2_reviews(self) -> G2Reviews:
        """G2 Software Product Reviews dataset - individual product reviews."""
        if self._g2_reviews is None:
            self._g2_reviews = G2Reviews(self._engine)
        return self._g2_reviews

    @property
    def trustpilot_reviews(self) -> TrustpilotReviews:
        """Trustpilot Business Reviews dataset - company reviews and ratings."""
        if self._trustpilot_reviews is None:
            self._trustpilot_reviews = TrustpilotReviews(self._engine)
        return self._trustpilot_reviews

    @property
    def indeed_companies(self) -> IndeedCompanies:
        """Indeed Companies Info dataset - company profiles with jobs and reviews."""
        if self._indeed_companies is None:
            self._indeed_companies = IndeedCompanies(self._engine)
        return self._indeed_companies

    @property
    def xing_profiles(self) -> XingProfiles:
        """Xing Social Network Profiles dataset - professional profiles."""
        if self._xing_profiles is None:
            self._xing_profiles = XingProfiles(self._engine)
        return self._xing_profiles

    @property
    def slintel_companies(self) -> SlintelCompanies:
        """Slintel 6sense Company Information dataset - technographics and company data."""
        if self._slintel_companies is None:
            self._slintel_companies = SlintelCompanies(self._engine)
        return self._slintel_companies

    @property
    def owler_companies(self) -> OwlerCompanies:
        """Owler Companies Information dataset - competitive intelligence and metrics."""
        if self._owler_companies is None:
            self._owler_companies = OwlerCompanies(self._engine)
        return self._owler_companies

    @property
    def us_lawyers(self) -> USLawyers:
        """US Lawyers Directory dataset - lawyer profiles and practice areas."""
        if self._us_lawyers is None:
            self._us_lawyers = USLawyers(self._engine)
        return self._us_lawyers

    @property
    def manta_businesses(self) -> MantaBusinesses:
        """Manta Businesses dataset - business listings with revenue and employees."""
        if self._manta_businesses is None:
            self._manta_businesses = MantaBusinesses(self._engine)
        return self._manta_businesses

    @property
    def ventureradar_companies(self) -> VentureRadarCompanies:
        """VentureRadar Company Information dataset - startup intelligence."""
        if self._ventureradar_companies is None:
            self._ventureradar_companies = VentureRadarCompanies(self._engine)
        return self._ventureradar_companies

    @property
    def trustradius_reviews(self) -> TrustRadiusReviews:
        """TrustRadius Product Reviews dataset - software product reviews."""
        if self._trustradius_reviews is None:
            self._trustradius_reviews = TrustRadiusReviews(self._engine)
        return self._trustradius_reviews

    @property
    def instagram_profiles(self) -> InstagramProfiles:
        """Instagram Profiles dataset - user profiles and engagement."""
        if self._instagram_profiles is None:
            self._instagram_profiles = InstagramProfiles(self._engine)
        return self._instagram_profiles

    @property
    def tiktok_profiles(self) -> TikTokProfiles:
        """TikTok Profiles dataset - user profiles and engagement."""
        if self._tiktok_profiles is None:
            self._tiktok_profiles = TikTokProfiles(self._engine)
        return self._tiktok_profiles

    @property
    def australia_real_estate(self) -> AustraliaRealEstate:
        """Australia Real Estate Properties dataset."""
        if self._australia_real_estate is None:
            self._australia_real_estate = AustraliaRealEstate(self._engine)
        return self._australia_real_estate

    @property
    def indeed_jobs(self) -> IndeedJobs:
        """Indeed Job Listings dataset."""
        if self._indeed_jobs is None:
            self._indeed_jobs = IndeedJobs(self._engine)
        return self._indeed_jobs

    @property
    def walmart_products(self) -> WalmartProducts:
        """Walmart Products dataset."""
        if self._walmart_products is None:
            self._walmart_products = WalmartProducts(self._engine)
        return self._walmart_products

    @property
    def mediamarkt_products(self) -> MediamarktProducts:
        """Mediamarkt.de Products dataset."""
        if self._mediamarkt_products is None:
            self._mediamarkt_products = MediamarktProducts(self._engine)
        return self._mediamarkt_products

    @property
    def fendi_products(self) -> FendiProducts:
        """Fendi Products dataset."""
        if self._fendi_products is None:
            self._fendi_products = FendiProducts(self._engine)
        return self._fendi_products

    @property
    def zalando_products(self) -> ZalandoProducts:
        """Zalando Products dataset."""
        if self._zalando_products is None:
            self._zalando_products = ZalandoProducts(self._engine)
        return self._zalando_products

    @property
    def sephora_products(self) -> SephoraProducts:
        """Sephora Products dataset."""
        if self._sephora_products is None:
            self._sephora_products = SephoraProducts(self._engine)
        return self._sephora_products

    @property
    def zara_products(self) -> ZaraProducts:
        """Zara Products dataset."""
        if self._zara_products is None:
            self._zara_products = ZaraProducts(self._engine)
        return self._zara_products

    @property
    def zara_home_products(self) -> ZaraHomeProducts:
        """Zara Home Products dataset."""
        if self._zara_home_products is None:
            self._zara_home_products = ZaraHomeProducts(self._engine)
        return self._zara_home_products

    @property
    def mango_products(self) -> MangoProducts:
        """Mango Products dataset."""
        if self._mango_products is None:
            self._mango_products = MangoProducts(self._engine)
        return self._mango_products

    @property
    def massimo_dutti_products(self) -> MassimoDuttiProducts:
        """Massimo Dutti Products dataset."""
        if self._massimo_dutti_products is None:
            self._massimo_dutti_products = MassimoDuttiProducts(self._engine)
        return self._massimo_dutti_products

    @property
    def otodom_poland(self) -> OtodomPoland:
        """Otodom Poland real estate dataset."""
        if self._otodom_poland is None:
            self._otodom_poland = OtodomPoland(self._engine)
        return self._otodom_poland

    @property
    def webmotors_brasil(self) -> WebmotorsBrasil:
        """Webmotors Brasil vehicle listings dataset."""
        if self._webmotors_brasil is None:
            self._webmotors_brasil = WebmotorsBrasil(self._engine)
        return self._webmotors_brasil

    @property
    def airbnb_properties(self) -> AirbnbProperties:
        """Airbnb Properties dataset."""
        if self._airbnb_properties is None:
            self._airbnb_properties = AirbnbProperties(self._engine)
        return self._airbnb_properties

    @property
    def asos_products(self) -> AsosProducts:
        """Asos Products dataset."""
        if self._asos_products is None:
            self._asos_products = AsosProducts(self._engine)
        return self._asos_products

    @property
    def chanel_products(self) -> ChanelProducts:
        """Chanel Products dataset."""
        if self._chanel_products is None:
            self._chanel_products = ChanelProducts(self._engine)
        return self._chanel_products

    @property
    def ashley_furniture_products(self) -> AshleyFurnitureProducts:
        """Ashley Furniture Products dataset."""
        if self._ashley_furniture_products is None:
            self._ashley_furniture_products = AshleyFurnitureProducts(self._engine)
        return self._ashley_furniture_products

    @property
    def fanatics_products(self) -> FanaticsProducts:
        """Fanatics Products dataset."""
        if self._fanatics_products is None:
            self._fanatics_products = FanaticsProducts(self._engine)
        return self._fanatics_products

    @property
    def carters_products(self) -> CartersProducts:
        """Carters Products dataset."""
        if self._carters_products is None:
            self._carters_products = CartersProducts(self._engine)
        return self._carters_products

    @property
    def american_eagle_products(self) -> AmericanEagleProducts:
        """American Eagle Products dataset."""
        if self._american_eagle_products is None:
            self._american_eagle_products = AmericanEagleProducts(self._engine)
        return self._american_eagle_products

    @property
    def ikea_products(self) -> IkeaProducts:
        """Ikea Products dataset."""
        if self._ikea_products is None:
            self._ikea_products = IkeaProducts(self._engine)
        return self._ikea_products

    @property
    def hm_products(self) -> HMProducts:
        """H&M Products dataset."""
        if self._hm_products is None:
            self._hm_products = HMProducts(self._engine)
        return self._hm_products

    @property
    def lego_products(self) -> LegoProducts:
        """Lego Products dataset."""
        if self._lego_products is None:
            self._lego_products = LegoProducts(self._engine)
        return self._lego_products

    @property
    def mattressfirm_products(self) -> MattressfirmProducts:
        """Mattressfirm Products dataset."""
        if self._mattressfirm_products is None:
            self._mattressfirm_products = MattressfirmProducts(self._engine)
        return self._mattressfirm_products

    @property
    def crateandbarrel_products(self) -> CrateAndBarrelProducts:
        """Crate and Barrel Products dataset."""
        if self._crateandbarrel_products is None:
            self._crateandbarrel_products = CrateAndBarrelProducts(self._engine)
        return self._crateandbarrel_products

    @property
    def llbean_products(self) -> LLBeanProducts:
        """L.L. Bean Products dataset."""
        if self._llbean_products is None:
            self._llbean_products = LLBeanProducts(self._engine)
        return self._llbean_products

    @property
    def shein_products(self) -> SheinProducts:
        """Shein Products dataset."""
        if self._shein_products is None:
            self._shein_products = SheinProducts(self._engine)
        return self._shein_products

    @property
    def toysrus_products(self) -> ToysRUsProducts:
        """Toys R Us Products dataset."""
        if self._toysrus_products is None:
            self._toysrus_products = ToysRUsProducts(self._engine)
        return self._toysrus_products

    @property
    def mybobs_products(self) -> MybobsProducts:
        """Mybobs Products dataset."""
        if self._mybobs_products is None:
            self._mybobs_products = MybobsProducts(self._engine)
        return self._mybobs_products

    @property
    def sleepnumber_products(self) -> SleepNumberProducts:
        """Sleep Number Products dataset."""
        if self._sleepnumber_products is None:
            self._sleepnumber_products = SleepNumberProducts(self._engine)
        return self._sleepnumber_products

    @property
    def raymourflanigan_products(self) -> RaymourFlaniganProducts:
        """Raymour and Flanigan Products dataset."""
        if self._raymourflanigan_products is None:
            self._raymourflanigan_products = RaymourFlaniganProducts(self._engine)
        return self._raymourflanigan_products

    @property
    def inmuebles24_mexico(self) -> Inmuebles24Mexico:
        """Inmuebles24 Mexico real estate dataset."""
        if self._inmuebles24_mexico is None:
            self._inmuebles24_mexico = Inmuebles24Mexico(self._engine)
        return self._inmuebles24_mexico

    @property
    def mouser_products(self) -> MouserProducts:
        """Mouser Products dataset."""
        if self._mouser_products is None:
            self._mouser_products = MouserProducts(self._engine)
        return self._mouser_products

    @property
    def zillow_properties(self) -> ZillowProperties:
        """Zillow Properties dataset."""
        if self._zillow_properties is None:
            self._zillow_properties = ZillowProperties(self._engine)
        return self._zillow_properties

    @property
    def zonaprop_argentina(self) -> ZonapropArgentina:
        """Zonaprop Argentina real estate dataset."""
        if self._zonaprop_argentina is None:
            self._zonaprop_argentina = ZonapropArgentina(self._engine)
        return self._zonaprop_argentina

    @property
    def metrocuadrado_properties(self) -> MetrocuadradoProperties:
        """Metrocuadrado Properties dataset."""
        if self._metrocuadrado_properties is None:
            self._metrocuadrado_properties = MetrocuadradoProperties(self._engine)
        return self._metrocuadrado_properties

    @property
    def chileautos_chile(self) -> ChileautosChile:
        """Chileautos Chile car listings dataset."""
        if self._chileautos_chile is None:
            self._chileautos_chile = ChileautosChile(self._engine)
        return self._chileautos_chile

    @property
    def infocasas_uruguay(self) -> InfocasasUruguay:
        """Infocasas Uruguay real estate dataset."""
        if self._infocasas_uruguay is None:
            self._infocasas_uruguay = InfocasasUruguay(self._engine)
        return self._infocasas_uruguay

    @property
    def lazboy_products(self) -> LaZBoyProducts:
        """La-Z-Boy Products dataset."""
        if self._lazboy_products is None:
            self._lazboy_products = LaZBoyProducts(self._engine)
        return self._lazboy_products

    @property
    def properati_properties(self) -> ProperatiProperties:
        """Properati Properties dataset."""
        if self._properati_properties is None:
            self._properati_properties = ProperatiProperties(self._engine)
        return self._properati_properties

    @property
    def yapo_chile(self) -> YapoChile:
        """Yapo Chile marketplace ads dataset."""
        if self._yapo_chile is None:
            self._yapo_chile = YapoChile(self._engine)
        return self._yapo_chile

    @property
    def toctoc_properties(self) -> ToctocProperties:
        """Toctoc Properties dataset."""
        if self._toctoc_properties is None:
            self._toctoc_properties = ToctocProperties(self._engine)
        return self._toctoc_properties

    @property
    def dior_products(self) -> DiorProducts:
        """Dior Products dataset."""
        if self._dior_products is None:
            self._dior_products = DiorProducts(self._engine)
        return self._dior_products

    @property
    def balenciaga_products(self) -> BalenciagaProducts:
        """Balenciaga Products dataset."""
        if self._balenciaga_products is None:
            self._balenciaga_products = BalenciagaProducts(self._engine)
        return self._balenciaga_products

    @property
    def bottegaveneta_products(self) -> BottegaVenetaProducts:
        """Bottega Veneta Products dataset."""
        if self._bottegaveneta_products is None:
            self._bottegaveneta_products = BottegaVenetaProducts(self._engine)
        return self._bottegaveneta_products

    @property
    def olx_brazil(self) -> OLXBrazil:
        """OLX Brazil marketplace ads dataset."""
        if self._olx_brazil is None:
            self._olx_brazil = OLXBrazil(self._engine)
        return self._olx_brazil

    @property
    def celine_products(self) -> CelineProducts:
        """Celine Products dataset."""
        if self._celine_products is None:
            self._celine_products = CelineProducts(self._engine)
        return self._celine_products

    @property
    def loewe_products(self) -> LoeweProducts:
        """Loewe Products dataset."""
        if self._loewe_products is None:
            self._loewe_products = LoeweProducts(self._engine)
        return self._loewe_products

    @property
    def berluti_products(self) -> BerlutiProducts:
        """Berluti Products dataset."""
        if self._berluti_products is None:
            self._berluti_products = BerlutiProducts(self._engine)
        return self._berluti_products

    @property
    def moynat_products(self) -> MoynatProducts:
        """Moynat Products dataset."""
        if self._moynat_products is None:
            self._moynat_products = MoynatProducts(self._engine)
        return self._moynat_products

    @property
    def hermes_products(self) -> HermesProducts:
        """Hermes Products dataset."""
        if self._hermes_products is None:
            self._hermes_products = HermesProducts(self._engine)
        return self._hermes_products

    @property
    def delvaux_products(self) -> DelvauxProducts:
        """Delvaux Products dataset."""
        if self._delvaux_products is None:
            self._delvaux_products = DelvauxProducts(self._engine)
        return self._delvaux_products

    @property
    def prada_products(self) -> PradaProducts:
        """Prada Products dataset."""
        if self._prada_products is None:
            self._prada_products = PradaProducts(self._engine)
        return self._prada_products

    @property
    def montblanc_products(self) -> MontblancProducts:
        """Montblanc Products dataset."""
        if self._montblanc_products is None:
            self._montblanc_products = MontblancProducts(self._engine)
        return self._montblanc_products

    @property
    def ysl_products(self) -> YSLProducts:
        """YSL Products dataset."""
        if self._ysl_products is None:
            self._ysl_products = YSLProducts(self._engine)
        return self._ysl_products

    @property
    def amazon_sellers_info(self) -> AmazonSellersInfo:
        """Amazon Sellers Info dataset."""
        if self._amazon_sellers_info is None:
            self._amazon_sellers_info = AmazonSellersInfo(self._engine)
        return self._amazon_sellers_info

    @property
    def world_zipcodes(self) -> WorldZipcodes:
        """World Zipcodes dataset."""
        if self._world_zipcodes is None:
            self._world_zipcodes = WorldZipcodes(self._engine)
        return self._world_zipcodes

    @property
    def pinterest_posts(self) -> PinterestPosts:
        """Pinterest Posts dataset."""
        if self._pinterest_posts is None:
            self._pinterest_posts = PinterestPosts(self._engine)
        return self._pinterest_posts

    @property
    def pinterest_profiles(self) -> PinterestProfiles:
        """Pinterest Profiles dataset."""
        if self._pinterest_profiles is None:
            self._pinterest_profiles = PinterestProfiles(self._engine)
        return self._pinterest_profiles

    @property
    def shopee_products(self) -> ShopeeProducts:
        """Shopee Products dataset."""
        if self._shopee_products is None:
            self._shopee_products = ShopeeProducts(self._engine)
        return self._shopee_products

    @property
    def lazada_products(self) -> LazadaProducts:
        """Lazada Products dataset."""
        if self._lazada_products is None:
            self._lazada_products = LazadaProducts(self._engine)
        return self._lazada_products

    @property
    def instagram_posts(self) -> InstagramPosts:
        """Instagram Posts dataset."""
        if self._instagram_posts is None:
            self._instagram_posts = InstagramPosts(self._engine)
        return self._instagram_posts

    @property
    def youtube_profiles(self) -> YouTubeProfiles:
        """YouTube Profiles dataset."""
        if self._youtube_profiles is None:
            self._youtube_profiles = YouTubeProfiles(self._engine)
        return self._youtube_profiles

    @property
    def youtube_videos(self) -> YouTubeVideos:
        """YouTube Videos dataset."""
        if self._youtube_videos is None:
            self._youtube_videos = YouTubeVideos(self._engine)
        return self._youtube_videos

    @property
    def youtube_comments(self) -> YouTubeComments:
        """YouTube Comments dataset."""
        if self._youtube_comments is None:
            self._youtube_comments = YouTubeComments(self._engine)
        return self._youtube_comments

    @property
    def digikey_products(self) -> DigikeyProducts:
        """Digikey Products dataset."""
        if self._digikey_products is None:
            self._digikey_products = DigikeyProducts(self._engine)
        return self._digikey_products

    @property
    def facebook_pages_posts(self) -> FacebookPagesPosts:
        """Facebook Pages Posts dataset."""
        if self._facebook_pages_posts is None:
            self._facebook_pages_posts = FacebookPagesPosts(self._engine)
        return self._facebook_pages_posts

    # --- New dataset properties - Social Media ---

    @property
    def facebook_comments(self) -> FacebookComments:
        """Facebook Comments dataset."""
        if self._facebook_comments is None:
            self._facebook_comments = FacebookComments(self._engine)
        return self._facebook_comments

    @property
    def facebook_posts_by_url(self) -> FacebookPostsByUrl:
        """Facebook Posts by URL dataset."""
        if self._facebook_posts_by_url is None:
            self._facebook_posts_by_url = FacebookPostsByUrl(self._engine)
        return self._facebook_posts_by_url

    @property
    def facebook_reels(self) -> FacebookReels:
        """Facebook Reels dataset."""
        if self._facebook_reels is None:
            self._facebook_reels = FacebookReels(self._engine)
        return self._facebook_reels

    @property
    def facebook_marketplace(self) -> FacebookMarketplace:
        """Facebook Marketplace dataset."""
        if self._facebook_marketplace is None:
            self._facebook_marketplace = FacebookMarketplace(self._engine)
        return self._facebook_marketplace

    @property
    def facebook_company_reviews(self) -> FacebookCompanyReviews:
        """Facebook Company Reviews dataset."""
        if self._facebook_company_reviews is None:
            self._facebook_company_reviews = FacebookCompanyReviews(self._engine)
        return self._facebook_company_reviews

    @property
    def facebook_events(self) -> FacebookEvents:
        """Facebook Events dataset."""
        if self._facebook_events is None:
            self._facebook_events = FacebookEvents(self._engine)
        return self._facebook_events

    @property
    def facebook_profiles(self) -> FacebookProfiles:
        """Facebook Profiles dataset."""
        if self._facebook_profiles is None:
            self._facebook_profiles = FacebookProfiles(self._engine)
        return self._facebook_profiles

    @property
    def facebook_pages_profiles(self) -> FacebookPagesProfiles:
        """Facebook Pages and Profiles dataset."""
        if self._facebook_pages_profiles is None:
            self._facebook_pages_profiles = FacebookPagesProfiles(self._engine)
        return self._facebook_pages_profiles

    @property
    def facebook_group_posts(self) -> FacebookGroupPosts:
        """Facebook Group Posts dataset."""
        if self._facebook_group_posts is None:
            self._facebook_group_posts = FacebookGroupPosts(self._engine)
        return self._facebook_group_posts

    @property
    def tiktok_comments(self) -> TikTokComments:
        """TikTok Comments dataset."""
        if self._tiktok_comments is None:
            self._tiktok_comments = TikTokComments(self._engine)
        return self._tiktok_comments

    @property
    def tiktok_posts(self) -> TikTokPosts:
        """TikTok Posts dataset."""
        if self._tiktok_posts is None:
            self._tiktok_posts = TikTokPosts(self._engine)
        return self._tiktok_posts

    @property
    def tiktok_shop(self) -> TikTokShop:
        """TikTok Shop dataset."""
        if self._tiktok_shop is None:
            self._tiktok_shop = TikTokShop(self._engine)
        return self._tiktok_shop

    @property
    def instagram_comments(self) -> InstagramComments:
        """Instagram Comments dataset."""
        if self._instagram_comments is None:
            self._instagram_comments = InstagramComments(self._engine)
        return self._instagram_comments

    @property
    def instagram_reels(self) -> InstagramReels:
        """Instagram Reels dataset."""
        if self._instagram_reels is None:
            self._instagram_reels = InstagramReels(self._engine)
        return self._instagram_reels

    @property
    def linkedin_posts(self) -> LinkedInPosts:
        """LinkedIn Posts dataset."""
        if self._linkedin_posts is None:
            self._linkedin_posts = LinkedInPosts(self._engine)
        return self._linkedin_posts

    @property
    def linkedin_profiles_job_listings(self) -> LinkedInProfilesJobListings:
        """LinkedIn Profiles Job Listings dataset."""
        if self._linkedin_profiles_job_listings is None:
            self._linkedin_profiles_job_listings = LinkedInProfilesJobListings(self._engine)
        return self._linkedin_profiles_job_listings

    @property
    def x_twitter_posts(self) -> XTwitterPosts:
        """X (Twitter) Posts dataset."""
        if self._x_twitter_posts is None:
            self._x_twitter_posts = XTwitterPosts(self._engine)
        return self._x_twitter_posts

    @property
    def x_twitter_profiles(self) -> XTwitterProfiles:
        """X (Twitter) Profiles dataset."""
        if self._x_twitter_profiles is None:
            self._x_twitter_profiles = XTwitterProfiles(self._engine)
        return self._x_twitter_profiles

    @property
    def reddit_posts(self) -> RedditPosts:
        """Reddit Posts dataset."""
        if self._reddit_posts is None:
            self._reddit_posts = RedditPosts(self._engine)
        return self._reddit_posts

    @property
    def reddit_comments(self) -> RedditComments:
        """Reddit Comments dataset."""
        if self._reddit_comments is None:
            self._reddit_comments = RedditComments(self._engine)
        return self._reddit_comments

    @property
    def bluesky_posts(self) -> BlueskyPosts:
        """Bluesky Posts dataset."""
        if self._bluesky_posts is None:
            self._bluesky_posts = BlueskyPosts(self._engine)
        return self._bluesky_posts

    @property
    def bluesky_top_profiles(self) -> BlueskyTopProfiles:
        """Top 500 Bluesky Profiles dataset."""
        if self._bluesky_top_profiles is None:
            self._bluesky_top_profiles = BlueskyTopProfiles(self._engine)
        return self._bluesky_top_profiles

    @property
    def snapchat_posts(self) -> SnapchatPosts:
        """Snapchat Posts dataset."""
        if self._snapchat_posts is None:
            self._snapchat_posts = SnapchatPosts(self._engine)
        return self._snapchat_posts

    @property
    def quora_posts(self) -> QuoraPosts:
        """Quora Posts dataset."""
        if self._quora_posts is None:
            self._quora_posts = QuoraPosts(self._engine)
        return self._quora_posts

    @property
    def vimeo_videos(self) -> VimeoVideos:
        """Vimeo Videos dataset."""
        if self._vimeo_videos is None:
            self._vimeo_videos = VimeoVideos(self._engine)
        return self._vimeo_videos

    # --- New dataset properties - News/Content ---

    @property
    def google_news(self) -> GoogleNews:
        """Google News dataset."""
        if self._google_news is None:
            self._google_news = GoogleNews(self._engine)
        return self._google_news

    @property
    def wikipedia_articles(self) -> WikipediaArticles:
        """Wikipedia Articles dataset."""
        if self._wikipedia_articles is None:
            self._wikipedia_articles = WikipediaArticles(self._engine)
        return self._wikipedia_articles

    @property
    def bbc_news(self) -> BBCNews:
        """BBC News dataset."""
        if self._bbc_news is None:
            self._bbc_news = BBCNews(self._engine)
        return self._bbc_news

    @property
    def cnn_news(self) -> CNNNews:
        """CNN News dataset."""
        if self._cnn_news is None:
            self._cnn_news = CNNNews(self._engine)
        return self._cnn_news

    @property
    def github_repositories(self) -> GithubRepositories:
        """GitHub Repositories dataset."""
        if self._github_repositories is None:
            self._github_repositories = GithubRepositories(self._engine)
        return self._github_repositories

    @property
    def creative_commons_images(self) -> CreativeCommonsImages:
        """Creative Commons Images dataset."""
        if self._creative_commons_images is None:
            self._creative_commons_images = CreativeCommonsImages(self._engine)
        return self._creative_commons_images

    @property
    def creative_commons_3d_models(self) -> CreativeCommons3DModels:
        """Creative Commons 3D Models dataset."""
        if self._creative_commons_3d_models is None:
            self._creative_commons_3d_models = CreativeCommons3DModels(self._engine)
        return self._creative_commons_3d_models

    # --- New dataset properties - App Stores ---

    @property
    def google_play_store(self) -> GooglePlayStore:
        """Google Play Store dataset."""
        if self._google_play_store is None:
            self._google_play_store = GooglePlayStore(self._engine)
        return self._google_play_store

    @property
    def google_play_reviews(self) -> GooglePlayReviews:
        """Google Play Store Reviews dataset."""
        if self._google_play_reviews is None:
            self._google_play_reviews = GooglePlayReviews(self._engine)
        return self._google_play_reviews

    @property
    def apple_app_store(self) -> AppleAppStore:
        """Apple App Store dataset."""
        if self._apple_app_store is None:
            self._apple_app_store = AppleAppStore(self._engine)
        return self._apple_app_store

    @property
    def apple_app_store_reviews(self) -> AppleAppStoreReviews:
        """Apple App Store Reviews dataset."""
        if self._apple_app_store_reviews is None:
            self._apple_app_store_reviews = AppleAppStoreReviews(self._engine)
        return self._apple_app_store_reviews

    # --- New dataset properties - E-commerce ---

    @property
    def amazon_best_sellers(self) -> AmazonBestSellers:
        """Amazon Best Sellers dataset."""
        if self._amazon_best_sellers is None:
            self._amazon_best_sellers = AmazonBestSellers(self._engine)
        return self._amazon_best_sellers

    @property
    def amazon_products_search(self) -> AmazonProductsSearch:
        """Amazon Products Search dataset."""
        if self._amazon_products_search is None:
            self._amazon_products_search = AmazonProductsSearch(self._engine)
        return self._amazon_products_search

    @property
    def amazon_products_global(self) -> AmazonProductsGlobal:
        """Amazon Products Global dataset."""
        if self._amazon_products_global is None:
            self._amazon_products_global = AmazonProductsGlobal(self._engine)
        return self._amazon_products_global

    @property
    def amazon_walmart(self) -> AmazonWalmart:
        """Amazon Walmart dataset."""
        if self._amazon_walmart is None:
            self._amazon_walmart = AmazonWalmart(self._engine)
        return self._amazon_walmart

    @property
    def walmart_sellers_info(self) -> WalmartSellersInfo:
        """Walmart Sellers Info dataset."""
        if self._walmart_sellers_info is None:
            self._walmart_sellers_info = WalmartSellersInfo(self._engine)
        return self._walmart_sellers_info

    @property
    def ebay_products(self) -> EbayProducts:
        """eBay Products dataset."""
        if self._ebay_products is None:
            self._ebay_products = EbayProducts(self._engine)
        return self._ebay_products

    @property
    def etsy_products(self) -> EtsyProducts:
        """Etsy Products dataset."""
        if self._etsy_products is None:
            self._etsy_products = EtsyProducts(self._engine)
        return self._etsy_products

    @property
    def target_products(self) -> TargetProducts:
        """Target Products dataset."""
        if self._target_products is None:
            self._target_products = TargetProducts(self._engine)
        return self._target_products

    @property
    def wayfair_products(self) -> WayfairProducts:
        """Wayfair Products dataset."""
        if self._wayfair_products is None:
            self._wayfair_products = WayfairProducts(self._engine)
        return self._wayfair_products

    @property
    def bestbuy_products(self) -> BestBuyProducts:
        """Best Buy Products dataset."""
        if self._bestbuy_products is None:
            self._bestbuy_products = BestBuyProducts(self._engine)
        return self._bestbuy_products

    @property
    def myntra_products(self) -> MyntraProducts:
        """Myntra Products dataset."""
        if self._myntra_products is None:
            self._myntra_products = MyntraProducts(self._engine)
        return self._myntra_products

    @property
    def ozon_products(self) -> OzonProducts:
        """Ozon.ru Products dataset."""
        if self._ozon_products is None:
            self._ozon_products = OzonProducts(self._engine)
        return self._ozon_products

    @property
    def wildberries_products(self) -> WildberriesProducts:
        """Wildberries.ru Products dataset."""
        if self._wildberries_products is None:
            self._wildberries_products = WildberriesProducts(self._engine)
        return self._wildberries_products

    @property
    def tokopedia_products(self) -> TokopediaProducts:
        """Tokopedia Products dataset."""
        if self._tokopedia_products is None:
            self._tokopedia_products = TokopediaProducts(self._engine)
        return self._tokopedia_products

    @property
    def google_shopping_products(self) -> GoogleShoppingProducts:
        """Google Shopping Products dataset."""
        if self._google_shopping_products is None:
            self._google_shopping_products = GoogleShoppingProducts(self._engine)
        return self._google_shopping_products

    @property
    def google_shopping_search_us(self) -> GoogleShoppingSearchUS:
        """Google Shopping Search US dataset."""
        if self._google_shopping_search_us is None:
            self._google_shopping_search_us = GoogleShoppingSearchUS(self._engine)
        return self._google_shopping_search_us

    @property
    def mercadolivre_products(self) -> MercadolivreProducts:
        """MercadoLivre Products dataset."""
        if self._mercadolivre_products is None:
            self._mercadolivre_products = MercadolivreProducts(self._engine)
        return self._mercadolivre_products

    @property
    def naver_products(self) -> NaverProducts:
        """Naver Products dataset."""
        if self._naver_products is None:
            self._naver_products = NaverProducts(self._engine)
        return self._naver_products

    @property
    def lazada_reviews(self) -> LazadaReviews:
        """Lazada Reviews dataset."""
        if self._lazada_reviews is None:
            self._lazada_reviews = LazadaReviews(self._engine)
        return self._lazada_reviews

    @property
    def lazada_products_search(self) -> LazadaProductsSearch:
        """Lazada Products Search dataset."""
        if self._lazada_products_search is None:
            self._lazada_products_search = LazadaProductsSearch(self._engine)
        return self._lazada_products_search

    @property
    def homedepot_us_products(self) -> HomeDepotUSProducts:
        """Home Depot US Products dataset."""
        if self._homedepot_us_products is None:
            self._homedepot_us_products = HomeDepotUSProducts(self._engine)
        return self._homedepot_us_products

    @property
    def homedepot_ca_products(self) -> HomeDepotCAProducts:
        """Home Depot Canada Products dataset."""
        if self._homedepot_ca_products is None:
            self._homedepot_ca_products = HomeDepotCAProducts(self._engine)
        return self._homedepot_ca_products

    @property
    def lowes_products(self) -> LowesProducts:
        """Lowes Products dataset."""
        if self._lowes_products is None:
            self._lowes_products = LowesProducts(self._engine)
        return self._lowes_products

    @property
    def rona_products(self) -> RonaProducts:
        """Rona.ca Products dataset."""
        if self._rona_products is None:
            self._rona_products = RonaProducts(self._engine)
        return self._rona_products

    @property
    def kroger_products(self) -> KrogerProducts:
        """Kroger Products dataset."""
        if self._kroger_products is None:
            self._kroger_products = KrogerProducts(self._engine)
        return self._kroger_products

    @property
    def macys_products(self) -> MacysProducts:
        """Macys Products dataset."""
        if self._macys_products is None:
            self._macys_products = MacysProducts(self._engine)
        return self._macys_products

    @property
    def costco_products(self) -> CostcoProducts:
        """Costco Products dataset."""
        if self._costco_products is None:
            self._costco_products = CostcoProducts(self._engine)
        return self._costco_products

    @property
    def bh_products(self) -> BHProducts:
        """B&H Products dataset."""
        if self._bh_products is None:
            self._bh_products = BHProducts(self._engine)
        return self._bh_products

    @property
    def microcenter_products(self) -> MicroCenterProducts:
        """Micro Center Products dataset."""
        if self._microcenter_products is None:
            self._microcenter_products = MicroCenterProducts(self._engine)
        return self._microcenter_products

    @property
    def autozone_products(self) -> AutozoneProducts:
        """AutoZone Products dataset."""
        if self._autozone_products is None:
            self._autozone_products = AutozoneProducts(self._engine)
        return self._autozone_products

    # --- New dataset properties - Real Estate/Travel ---

    @property
    def zillow_price_history(self) -> ZillowPriceHistory:
        """Zillow Price History dataset."""
        if self._zillow_price_history is None:
            self._zillow_price_history = ZillowPriceHistory(self._engine)
        return self._zillow_price_history

    @property
    def zoopla_properties(self) -> ZooplaProperties:
        """Zoopla Properties dataset."""
        if self._zoopla_properties is None:
            self._zoopla_properties = ZooplaProperties(self._engine)
        return self._zoopla_properties

    @property
    def booking_listings_search(self) -> BookingListingsSearch:
        """Booking.com Listings Search dataset."""
        if self._booking_listings_search is None:
            self._booking_listings_search = BookingListingsSearch(self._engine)
        return self._booking_listings_search

    @property
    def booking_hotel_listings(self) -> BookingHotelListings:
        """Booking.com Hotel Listings dataset."""
        if self._booking_hotel_listings is None:
            self._booking_hotel_listings = BookingHotelListings(self._engine)
        return self._booking_hotel_listings

    @property
    def realtor_international_properties(self) -> RealtorInternationalProperties:
        """Realtor International Properties dataset."""
        if self._realtor_international_properties is None:
            self._realtor_international_properties = RealtorInternationalProperties(self._engine)
        return self._realtor_international_properties

    @property
    def agoda_properties(self) -> AgodaProperties:
        """Agoda Properties dataset."""
        if self._agoda_properties is None:
            self._agoda_properties = AgodaProperties(self._engine)
        return self._agoda_properties

    @property
    def carsales_listings(self) -> CarsalesListings:
        """Carsales Car Listings dataset."""
        if self._carsales_listings is None:
            self._carsales_listings = CarsalesListings(self._engine)
        return self._carsales_listings

    # --- New dataset properties - Finance/Maps ---

    @property
    def yahoo_finance_businesses(self) -> YahooFinanceBusinesses:
        """Yahoo Finance Businesses dataset."""
        if self._yahoo_finance_businesses is None:
            self._yahoo_finance_businesses = YahooFinanceBusinesses(self._engine)
        return self._yahoo_finance_businesses

    @property
    def google_maps_full_info(self) -> GoogleMapsFullInfo:
        """Google Maps Full Info dataset."""
        if self._google_maps_full_info is None:
            self._google_maps_full_info = GoogleMapsFullInfo(self._engine)
        return self._google_maps_full_info
