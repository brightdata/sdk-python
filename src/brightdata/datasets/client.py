"""
Datasets client - main entry point for datasets API.
"""

from typing import List, Optional, TYPE_CHECKING

from .models import DatasetInfo
from .linkedin import LinkedInPeopleProfiles, LinkedInCompanyProfiles, LinkedInJobListings
from .amazon import AmazonProducts, AmazonReviews, AmazonSellersInfo
from .crunchbase import CrunchbaseCompanies
from .imdb import IMDBMovies
from .nba import NBAPlayersStats
from .goodreads import GoodreadsBooks
from .world_population import WorldPopulation
from .companies_enriched import CompaniesEnriched
from .employees_enriched import EmployeesEnriched
from .glassdoor import GlassdoorCompanies, GlassdoorReviews, GlassdoorJobs
from .google_maps import GoogleMapsReviews
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
from .instagram import InstagramProfiles, InstagramPosts
from .tiktok import TikTokProfiles
from .real_estate import AustraliaRealEstate
from .walmart import WalmartProducts
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
from .zillow import ZillowProperties
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
from .lazada import LazadaProducts
from .youtube import YouTubeProfiles, YouTubeVideos, YouTubeComments
from .digikey import DigikeyProducts
from .facebook import FacebookPagesPosts

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
