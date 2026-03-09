"""Type stub for DatasetsClient — provides IDE autocomplete."""

from typing import List
from .models import DatasetInfo
from ..core.engine import AsyncEngine

from .agoda import AgodaProperties
from .airbnb import AirbnbProperties
from .amazon import (
    AmazonBestSellers,
    AmazonProducts,
    AmazonProductsGlobal,
    AmazonProductsSearch,
    AmazonReviews,
    AmazonSellersInfo,
    AmazonWalmart,
)
from .american_eagle import AmericanEagleProducts
from .apple_appstore import (
    AppleAppStore,
    AppleAppStoreReviews,
)
from .ashley_furniture import AshleyFurnitureProducts
from .asos import AsosProducts
from .autozone import AutozoneProducts
from .balenciaga import BalenciagaProducts
from .bbc import BBCNews
from .berluti import BerlutiProducts
from .bestbuy import BestBuyProducts
from .bh import BHProducts
from .bluesky import (
    BlueskyPosts,
    BlueskyTopProfiles,
)
from .booking import (
    BookingHotelListings,
    BookingListingsSearch,
)
from .bottegaveneta import BottegaVenetaProducts
from .carsales import CarsalesListings
from .carters import CartersProducts
from .celine import CelineProducts
from .chanel import ChanelProducts
from .chileautos import ChileautosChile
from .cnn import CNNNews
from .companies_enriched import CompaniesEnriched
from .costco import CostcoProducts
from .crateandbarrel import CrateAndBarrelProducts
from .creative_commons import (
    CreativeCommons3DModels,
    CreativeCommonsImages,
)
from .crunchbase import CrunchbaseCompanies
from .delvaux import DelvauxProducts
from .digikey import DigikeyProducts
from .dior import DiorProducts
from .ebay import EbayProducts
from .employees_enriched import EmployeesEnriched
from .etsy import EtsyProducts
from .facebook import (
    FacebookComments,
    FacebookCompanyReviews,
    FacebookEvents,
    FacebookGroupPosts,
    FacebookMarketplace,
    FacebookPagesPosts,
    FacebookPagesProfiles,
    FacebookPostsByUrl,
    FacebookProfiles,
    FacebookReels,
)
from .fanatics import FanaticsProducts
from .fendi import FendiProducts
from .g2 import (
    G2Products,
    G2Reviews,
)
from .github import GithubRepositories
from .glassdoor import (
    GlassdoorCompanies,
    GlassdoorJobs,
    GlassdoorReviews,
)
from .goodreads import GoodreadsBooks
from .google_maps import (
    GoogleMapsFullInfo,
    GoogleMapsReviews,
)
from .google_news import GoogleNews
from .google_play import (
    GooglePlayReviews,
    GooglePlayStore,
)
from .google_shopping import (
    GoogleShoppingProducts,
    GoogleShoppingSearchUS,
)
from .hermes import HermesProducts
from .hm import HMProducts
from .homedepot import (
    HomeDepotCAProducts,
    HomeDepotUSProducts,
)
from .ikea import IkeaProducts
from .imdb import IMDBMovies
from .indeed import (
    IndeedCompanies,
    IndeedJobs,
)
from .infocasas import InfocasasUruguay
from .inmuebles24 import Inmuebles24Mexico
from .instagram import (
    InstagramComments,
    InstagramPosts,
    InstagramProfiles,
    InstagramReels,
)
from .kroger import KrogerProducts
from .lawyers import USLawyers
from .lazada import (
    LazadaProducts,
    LazadaProductsSearch,
    LazadaReviews,
)
from .lazboy import LaZBoyProducts
from .lego import LegoProducts
from .linkedin import (
    LinkedInCompanyProfiles,
    LinkedInJobListings,
    LinkedInPeopleProfiles,
    LinkedInPosts,
    LinkedInProfilesJobListings,
)
from .llbean import LLBeanProducts
from .loewe import LoeweProducts
from .lowes import LowesProducts
from .macys import MacysProducts
from .mango import MangoProducts
from .manta import MantaBusinesses
from .massimo_dutti import MassimoDuttiProducts
from .mattressfirm import MattressfirmProducts
from .mediamarkt import MediamarktProducts
from .mercadolivre import MercadolivreProducts
from .metrocuadrado import MetrocuadradoProperties
from .microcenter import MicroCenterProducts
from .montblanc import MontblancProducts
from .mouser import MouserProducts
from .moynat import MoynatProducts
from .mybobs import MybobsProducts
from .myntra import MyntraProducts
from .naver import NaverProducts
from .nba import NBAPlayersStats
from .olx import OLXBrazil
from .otodom import OtodomPoland
from .owler import OwlerCompanies
from .ozon import OzonProducts
from .pinterest import (
    PinterestPosts,
    PinterestProfiles,
)
from .pitchbook import PitchBookCompanies
from .prada import PradaProducts
from .properati import ProperatiProperties
from .quora import QuoraPosts
from .raymourflanigan import RaymourFlaniganProducts
from .real_estate import AustraliaRealEstate
from .realtor import RealtorInternationalProperties
from .reddit import (
    RedditComments,
    RedditPosts,
)
from .rona import RonaProducts
from .sephora import SephoraProducts
from .shein import SheinProducts
from .shopee import ShopeeProducts
from .sleepnumber import SleepNumberProducts
from .slintel import SlintelCompanies
from .snapchat import SnapchatPosts
from .tiktok import (
    TikTokComments,
    TikTokPosts,
    TikTokProfiles,
    TikTokShop,
)
from .toctoc import ToctocProperties
from .tokopedia import TokopediaProducts
from .toysrus import ToysRUsProducts
from .trustpilot import TrustpilotReviews
from .trustradius import TrustRadiusReviews
from .ventureradar import VentureRadarCompanies
from .vimeo import VimeoVideos
from .walmart import (
    WalmartProducts,
    WalmartSellersInfo,
)
from .wayfair import WayfairProducts
from .webmotors import WebmotorsBrasil
from .wikipedia import WikipediaArticles
from .wildberries import WildberriesProducts
from .world_population import WorldPopulation
from .world_zipcodes import WorldZipcodes
from .x_twitter import (
    XTwitterPosts,
    XTwitterProfiles,
)
from .xing import XingProfiles
from .yahoo_finance import YahooFinanceBusinesses
from .yapo import YapoChile
from .yelp import (
    YelpBusinesses,
    YelpReviews,
)
from .youtube import (
    YouTubeComments,
    YouTubeProfiles,
    YouTubeVideos,
)
from .ysl import YSLProducts
from .zalando import ZalandoProducts
from .zara import (
    ZaraHomeProducts,
    ZaraProducts,
)
from .zillow import (
    ZillowPriceHistory,
    ZillowProperties,
)
from .zonaprop import ZonapropArgentina
from .zoominfo import ZoomInfoCompanies
from .zoopla import ZooplaProperties

class DatasetsClient:
    BASE_URL: str

    def __init__(self, engine: AsyncEngine) -> None: ...
    async def list(self) -> List[DatasetInfo]: ...
    @property
    def linkedin_profiles(self) -> LinkedInPeopleProfiles:
        """LinkedIn People Profiles dataset (620M+ records)."""
        ...

    @property
    def linkedin_companies(self) -> LinkedInCompanyProfiles:
        """LinkedIn Company Profiles dataset."""
        ...

    @property
    def linkedin_job_listings(self) -> LinkedInJobListings:
        """LinkedIn Profiles Jobs Listings dataset."""
        ...

    @property
    def amazon_products(self) -> AmazonProducts:
        """Amazon Products dataset."""
        ...

    @property
    def amazon_reviews(self) -> AmazonReviews:
        """Amazon Reviews dataset."""
        ...

    @property
    def crunchbase_companies(self) -> CrunchbaseCompanies:
        """Crunchbase Companies dataset (2.3M+ records)."""
        ...

    @property
    def imdb_movies(self) -> IMDBMovies:
        """IMDB Movies dataset (867K+ records)."""
        ...

    @property
    def nba_players_stats(self) -> NBAPlayersStats:
        """NBA Players Stats dataset (17K+ records)."""
        ...

    @property
    def goodreads_books(self) -> GoodreadsBooks:
        """Goodreads Books dataset."""
        ...

    @property
    def world_population(self) -> WorldPopulation:
        """World Population dataset."""
        ...

    @property
    def companies_enriched(self) -> CompaniesEnriched:
        """Companies Enriched dataset - multi-source company information."""
        ...

    @property
    def employees_enriched(self) -> EmployeesEnriched:
        """Employees Business Enriched dataset - LinkedIn profiles with company data."""
        ...

    @property
    def glassdoor_companies(self) -> GlassdoorCompanies:
        """Glassdoor Companies Overview dataset - ratings, reviews, and company details."""
        ...

    @property
    def glassdoor_reviews(self) -> GlassdoorReviews:
        """Glassdoor Companies Reviews dataset - employee reviews and ratings."""
        ...

    @property
    def glassdoor_jobs(self) -> GlassdoorJobs:
        """Glassdoor Job Listings dataset - job postings with company data."""
        ...

    @property
    def google_maps_reviews(self) -> GoogleMapsReviews:
        """Google Maps Reviews dataset - place reviews and ratings."""
        ...

    @property
    def yelp_businesses(self) -> YelpBusinesses:
        """Yelp Businesses Overview dataset - business listings and ratings."""
        ...

    @property
    def yelp_reviews(self) -> YelpReviews:
        """Yelp Business Reviews dataset - individual business reviews."""
        ...

    @property
    def zoominfo_companies(self) -> ZoomInfoCompanies:
        """ZoomInfo Companies dataset - company data with financials and contacts."""
        ...

    @property
    def pitchbook_companies(self) -> PitchBookCompanies:
        """PitchBook Companies dataset - PE/VC company data with deals."""
        ...

    @property
    def g2_products(self) -> G2Products:
        """G2 Software Product Overview dataset - software ratings and reviews."""
        ...

    @property
    def g2_reviews(self) -> G2Reviews:
        """G2 Software Product Reviews dataset - individual product reviews."""
        ...

    @property
    def trustpilot_reviews(self) -> TrustpilotReviews:
        """Trustpilot Business Reviews dataset - company reviews and ratings."""
        ...

    @property
    def indeed_companies(self) -> IndeedCompanies:
        """Indeed Companies Info dataset - company profiles with jobs and reviews."""
        ...

    @property
    def xing_profiles(self) -> XingProfiles:
        """Xing Social Network Profiles dataset - professional profiles."""
        ...

    @property
    def slintel_companies(self) -> SlintelCompanies:
        """Slintel 6sense Company Information dataset - technographics and company data."""
        ...

    @property
    def owler_companies(self) -> OwlerCompanies:
        """Owler Companies Information dataset - competitive intelligence and metrics."""
        ...

    @property
    def us_lawyers(self) -> USLawyers:
        """US Lawyers Directory dataset - lawyer profiles and practice areas."""
        ...

    @property
    def manta_businesses(self) -> MantaBusinesses:
        """Manta Businesses dataset - business listings with revenue and employees."""
        ...

    @property
    def ventureradar_companies(self) -> VentureRadarCompanies:
        """VentureRadar Company Information dataset - startup intelligence."""
        ...

    @property
    def trustradius_reviews(self) -> TrustRadiusReviews:
        """TrustRadius Product Reviews dataset - software product reviews."""
        ...

    @property
    def instagram_profiles(self) -> InstagramProfiles:
        """Instagram Profiles dataset - user profiles and engagement."""
        ...

    @property
    def tiktok_profiles(self) -> TikTokProfiles:
        """TikTok Profiles dataset - user profiles and engagement."""
        ...

    @property
    def australia_real_estate(self) -> AustraliaRealEstate:
        """Australia Real Estate Properties dataset."""
        ...

    @property
    def indeed_jobs(self) -> IndeedJobs:
        """Indeed Job Listings dataset."""
        ...

    @property
    def walmart_products(self) -> WalmartProducts:
        """Walmart Products dataset."""
        ...

    @property
    def mediamarkt_products(self) -> MediamarktProducts:
        """Mediamarkt.de Products dataset."""
        ...

    @property
    def fendi_products(self) -> FendiProducts:
        """Fendi Products dataset."""
        ...

    @property
    def zalando_products(self) -> ZalandoProducts:
        """Zalando Products dataset."""
        ...

    @property
    def sephora_products(self) -> SephoraProducts:
        """Sephora Products dataset."""
        ...

    @property
    def zara_products(self) -> ZaraProducts:
        """Zara Products dataset."""
        ...

    @property
    def zara_home_products(self) -> ZaraHomeProducts:
        """Zara Home Products dataset."""
        ...

    @property
    def mango_products(self) -> MangoProducts:
        """Mango Products dataset."""
        ...

    @property
    def massimo_dutti_products(self) -> MassimoDuttiProducts:
        """Massimo Dutti Products dataset."""
        ...

    @property
    def otodom_poland(self) -> OtodomPoland:
        """Otodom Poland real estate dataset."""
        ...

    @property
    def webmotors_brasil(self) -> WebmotorsBrasil:
        """Webmotors Brasil vehicle listings dataset."""
        ...

    @property
    def airbnb_properties(self) -> AirbnbProperties:
        """Airbnb Properties dataset."""
        ...

    @property
    def asos_products(self) -> AsosProducts:
        """Asos Products dataset."""
        ...

    @property
    def chanel_products(self) -> ChanelProducts:
        """Chanel Products dataset."""
        ...

    @property
    def ashley_furniture_products(self) -> AshleyFurnitureProducts:
        """Ashley Furniture Products dataset."""
        ...

    @property
    def fanatics_products(self) -> FanaticsProducts:
        """Fanatics Products dataset."""
        ...

    @property
    def carters_products(self) -> CartersProducts:
        """Carters Products dataset."""
        ...

    @property
    def american_eagle_products(self) -> AmericanEagleProducts:
        """American Eagle Products dataset."""
        ...

    @property
    def ikea_products(self) -> IkeaProducts:
        """Ikea Products dataset."""
        ...

    @property
    def hm_products(self) -> HMProducts:
        """H&M Products dataset."""
        ...

    @property
    def lego_products(self) -> LegoProducts:
        """Lego Products dataset."""
        ...

    @property
    def mattressfirm_products(self) -> MattressfirmProducts:
        """Mattressfirm Products dataset."""
        ...

    @property
    def crateandbarrel_products(self) -> CrateAndBarrelProducts:
        """Crate and Barrel Products dataset."""
        ...

    @property
    def llbean_products(self) -> LLBeanProducts:
        """L.L. Bean Products dataset."""
        ...

    @property
    def shein_products(self) -> SheinProducts:
        """Shein Products dataset."""
        ...

    @property
    def toysrus_products(self) -> ToysRUsProducts:
        """Toys R Us Products dataset."""
        ...

    @property
    def mybobs_products(self) -> MybobsProducts:
        """Mybobs Products dataset."""
        ...

    @property
    def sleepnumber_products(self) -> SleepNumberProducts:
        """Sleep Number Products dataset."""
        ...

    @property
    def raymourflanigan_products(self) -> RaymourFlaniganProducts:
        """Raymour and Flanigan Products dataset."""
        ...

    @property
    def inmuebles24_mexico(self) -> Inmuebles24Mexico:
        """Inmuebles24 Mexico real estate dataset."""
        ...

    @property
    def mouser_products(self) -> MouserProducts:
        """Mouser Products dataset."""
        ...

    @property
    def zillow_properties(self) -> ZillowProperties:
        """Zillow Properties dataset."""
        ...

    @property
    def zonaprop_argentina(self) -> ZonapropArgentina:
        """Zonaprop Argentina real estate dataset."""
        ...

    @property
    def metrocuadrado_properties(self) -> MetrocuadradoProperties:
        """Metrocuadrado Properties dataset."""
        ...

    @property
    def chileautos_chile(self) -> ChileautosChile:
        """Chileautos Chile car listings dataset."""
        ...

    @property
    def infocasas_uruguay(self) -> InfocasasUruguay:
        """Infocasas Uruguay real estate dataset."""
        ...

    @property
    def lazboy_products(self) -> LaZBoyProducts:
        """La-Z-Boy Products dataset."""
        ...

    @property
    def properati_properties(self) -> ProperatiProperties:
        """Properati Properties dataset."""
        ...

    @property
    def yapo_chile(self) -> YapoChile:
        """Yapo Chile marketplace ads dataset."""
        ...

    @property
    def toctoc_properties(self) -> ToctocProperties:
        """Toctoc Properties dataset."""
        ...

    @property
    def dior_products(self) -> DiorProducts:
        """Dior Products dataset."""
        ...

    @property
    def balenciaga_products(self) -> BalenciagaProducts:
        """Balenciaga Products dataset."""
        ...

    @property
    def bottegaveneta_products(self) -> BottegaVenetaProducts:
        """Bottega Veneta Products dataset."""
        ...

    @property
    def olx_brazil(self) -> OLXBrazil:
        """OLX Brazil marketplace ads dataset."""
        ...

    @property
    def celine_products(self) -> CelineProducts:
        """Celine Products dataset."""
        ...

    @property
    def loewe_products(self) -> LoeweProducts:
        """Loewe Products dataset."""
        ...

    @property
    def berluti_products(self) -> BerlutiProducts:
        """Berluti Products dataset."""
        ...

    @property
    def moynat_products(self) -> MoynatProducts:
        """Moynat Products dataset."""
        ...

    @property
    def hermes_products(self) -> HermesProducts:
        """Hermes Products dataset."""
        ...

    @property
    def delvaux_products(self) -> DelvauxProducts:
        """Delvaux Products dataset."""
        ...

    @property
    def prada_products(self) -> PradaProducts:
        """Prada Products dataset."""
        ...

    @property
    def montblanc_products(self) -> MontblancProducts:
        """Montblanc Products dataset."""
        ...

    @property
    def ysl_products(self) -> YSLProducts:
        """YSL Products dataset."""
        ...

    @property
    def amazon_sellers_info(self) -> AmazonSellersInfo:
        """Amazon Sellers Info dataset."""
        ...

    @property
    def world_zipcodes(self) -> WorldZipcodes:
        """World Zipcodes dataset."""
        ...

    @property
    def pinterest_posts(self) -> PinterestPosts:
        """Pinterest Posts dataset."""
        ...

    @property
    def pinterest_profiles(self) -> PinterestProfiles:
        """Pinterest Profiles dataset."""
        ...

    @property
    def shopee_products(self) -> ShopeeProducts:
        """Shopee Products dataset."""
        ...

    @property
    def lazada_products(self) -> LazadaProducts:
        """Lazada Products dataset."""
        ...

    @property
    def instagram_posts(self) -> InstagramPosts:
        """Instagram Posts dataset."""
        ...

    @property
    def youtube_profiles(self) -> YouTubeProfiles:
        """YouTube Profiles dataset."""
        ...

    @property
    def youtube_videos(self) -> YouTubeVideos:
        """YouTube Videos dataset."""
        ...

    @property
    def youtube_comments(self) -> YouTubeComments:
        """YouTube Comments dataset."""
        ...

    @property
    def digikey_products(self) -> DigikeyProducts:
        """Digikey Products dataset."""
        ...

    @property
    def facebook_pages_posts(self) -> FacebookPagesPosts:
        """Facebook Pages Posts dataset."""
        ...

    @property
    def facebook_comments(self) -> FacebookComments:
        """Facebook Comments dataset."""
        ...

    @property
    def facebook_posts_by_url(self) -> FacebookPostsByUrl:
        """Facebook Posts by URL dataset."""
        ...

    @property
    def facebook_reels(self) -> FacebookReels:
        """Facebook Reels dataset."""
        ...

    @property
    def facebook_marketplace(self) -> FacebookMarketplace:
        """Facebook Marketplace dataset."""
        ...

    @property
    def facebook_company_reviews(self) -> FacebookCompanyReviews:
        """Facebook Company Reviews dataset."""
        ...

    @property
    def facebook_events(self) -> FacebookEvents:
        """Facebook Events dataset."""
        ...

    @property
    def facebook_profiles(self) -> FacebookProfiles:
        """Facebook Profiles dataset."""
        ...

    @property
    def facebook_pages_profiles(self) -> FacebookPagesProfiles:
        """Facebook Pages and Profiles dataset."""
        ...

    @property
    def facebook_group_posts(self) -> FacebookGroupPosts:
        """Facebook Group Posts dataset."""
        ...

    @property
    def tiktok_comments(self) -> TikTokComments:
        """TikTok Comments dataset."""
        ...

    @property
    def tiktok_posts(self) -> TikTokPosts:
        """TikTok Posts dataset."""
        ...

    @property
    def tiktok_shop(self) -> TikTokShop:
        """TikTok Shop dataset."""
        ...

    @property
    def instagram_comments(self) -> InstagramComments:
        """Instagram Comments dataset."""
        ...

    @property
    def instagram_reels(self) -> InstagramReels:
        """Instagram Reels dataset."""
        ...

    @property
    def linkedin_posts(self) -> LinkedInPosts:
        """LinkedIn Posts dataset."""
        ...

    @property
    def linkedin_profiles_job_listings(self) -> LinkedInProfilesJobListings:
        """LinkedIn Profiles Job Listings dataset."""
        ...

    @property
    def x_twitter_posts(self) -> XTwitterPosts:
        """X (Twitter) Posts dataset."""
        ...

    @property
    def x_twitter_profiles(self) -> XTwitterProfiles:
        """X (Twitter) Profiles dataset."""
        ...

    @property
    def reddit_posts(self) -> RedditPosts:
        """Reddit Posts dataset."""
        ...

    @property
    def reddit_comments(self) -> RedditComments:
        """Reddit Comments dataset."""
        ...

    @property
    def bluesky_posts(self) -> BlueskyPosts:
        """Bluesky Posts dataset."""
        ...

    @property
    def bluesky_top_profiles(self) -> BlueskyTopProfiles:
        """Top 500 Bluesky Profiles dataset."""
        ...

    @property
    def snapchat_posts(self) -> SnapchatPosts:
        """Snapchat Posts dataset."""
        ...

    @property
    def quora_posts(self) -> QuoraPosts:
        """Quora Posts dataset."""
        ...

    @property
    def vimeo_videos(self) -> VimeoVideos:
        """Vimeo Videos dataset."""
        ...

    @property
    def google_news(self) -> GoogleNews:
        """Google News dataset."""
        ...

    @property
    def wikipedia_articles(self) -> WikipediaArticles:
        """Wikipedia Articles dataset."""
        ...

    @property
    def bbc_news(self) -> BBCNews:
        """BBC News dataset."""
        ...

    @property
    def cnn_news(self) -> CNNNews:
        """CNN News dataset."""
        ...

    @property
    def github_repositories(self) -> GithubRepositories:
        """GitHub Repositories dataset."""
        ...

    @property
    def creative_commons_images(self) -> CreativeCommonsImages:
        """Creative Commons Images dataset."""
        ...

    @property
    def creative_commons_3d_models(self) -> CreativeCommons3DModels:
        """Creative Commons 3D Models dataset."""
        ...

    @property
    def google_play_store(self) -> GooglePlayStore:
        """Google Play Store dataset."""
        ...

    @property
    def google_play_reviews(self) -> GooglePlayReviews:
        """Google Play Store Reviews dataset."""
        ...

    @property
    def apple_app_store(self) -> AppleAppStore:
        """Apple App Store dataset."""
        ...

    @property
    def apple_app_store_reviews(self) -> AppleAppStoreReviews:
        """Apple App Store Reviews dataset."""
        ...

    @property
    def amazon_best_sellers(self) -> AmazonBestSellers:
        """Amazon Best Sellers dataset."""
        ...

    @property
    def amazon_products_search(self) -> AmazonProductsSearch:
        """Amazon Products Search dataset."""
        ...

    @property
    def amazon_products_global(self) -> AmazonProductsGlobal:
        """Amazon Products Global dataset."""
        ...

    @property
    def amazon_walmart(self) -> AmazonWalmart:
        """Amazon Walmart dataset."""
        ...

    @property
    def walmart_sellers_info(self) -> WalmartSellersInfo:
        """Walmart Sellers Info dataset."""
        ...

    @property
    def ebay_products(self) -> EbayProducts:
        """eBay Products dataset."""
        ...

    @property
    def etsy_products(self) -> EtsyProducts:
        """Etsy Products dataset."""
        ...

    @property
    def wayfair_products(self) -> WayfairProducts:
        """Wayfair Products dataset."""
        ...

    @property
    def bestbuy_products(self) -> BestBuyProducts:
        """Best Buy Products dataset."""
        ...

    @property
    def myntra_products(self) -> MyntraProducts:
        """Myntra Products dataset."""
        ...

    @property
    def ozon_products(self) -> OzonProducts:
        """Ozon.ru Products dataset."""
        ...

    @property
    def wildberries_products(self) -> WildberriesProducts:
        """Wildberries.ru Products dataset."""
        ...

    @property
    def tokopedia_products(self) -> TokopediaProducts:
        """Tokopedia Products dataset."""
        ...

    @property
    def google_shopping_products(self) -> GoogleShoppingProducts:
        """Google Shopping Products dataset."""
        ...

    @property
    def google_shopping_search_us(self) -> GoogleShoppingSearchUS:
        """Google Shopping Search US dataset."""
        ...

    @property
    def mercadolivre_products(self) -> MercadolivreProducts:
        """MercadoLivre Products dataset."""
        ...

    @property
    def naver_products(self) -> NaverProducts:
        """Naver Products dataset."""
        ...

    @property
    def lazada_reviews(self) -> LazadaReviews:
        """Lazada Reviews dataset."""
        ...

    @property
    def lazada_products_search(self) -> LazadaProductsSearch:
        """Lazada Products Search dataset."""
        ...

    @property
    def homedepot_us_products(self) -> HomeDepotUSProducts:
        """Home Depot US Products dataset."""
        ...

    @property
    def homedepot_ca_products(self) -> HomeDepotCAProducts:
        """Home Depot Canada Products dataset."""
        ...

    @property
    def lowes_products(self) -> LowesProducts:
        """Lowes Products dataset."""
        ...

    @property
    def rona_products(self) -> RonaProducts:
        """Rona.ca Products dataset."""
        ...

    @property
    def kroger_products(self) -> KrogerProducts:
        """Kroger Products dataset."""
        ...

    @property
    def macys_products(self) -> MacysProducts:
        """Macys Products dataset."""
        ...

    @property
    def costco_products(self) -> CostcoProducts:
        """Costco Products dataset."""
        ...

    @property
    def bh_products(self) -> BHProducts:
        """B&H Products dataset."""
        ...

    @property
    def microcenter_products(self) -> MicroCenterProducts:
        """Micro Center Products dataset."""
        ...

    @property
    def autozone_products(self) -> AutozoneProducts:
        """AutoZone Products dataset."""
        ...

    @property
    def zillow_price_history(self) -> ZillowPriceHistory:
        """Zillow Price History dataset."""
        ...

    @property
    def zoopla_properties(self) -> ZooplaProperties:
        """Zoopla Properties dataset."""
        ...

    @property
    def booking_listings_search(self) -> BookingListingsSearch:
        """Booking.com Listings Search dataset."""
        ...

    @property
    def booking_hotel_listings(self) -> BookingHotelListings:
        """Booking.com Hotel Listings dataset."""
        ...

    @property
    def realtor_international_properties(self) -> RealtorInternationalProperties:
        """Realtor International Properties dataset."""
        ...

    @property
    def agoda_properties(self) -> AgodaProperties:
        """Agoda Properties dataset."""
        ...

    @property
    def carsales_listings(self) -> CarsalesListings:
        """Carsales Car Listings dataset."""
        ...

    @property
    def yahoo_finance_businesses(self) -> YahooFinanceBusinesses:
        """Yahoo Finance Businesses dataset."""
        ...

    @property
    def google_maps_full_info(self) -> GoogleMapsFullInfo:
        """Google Maps Full Info dataset."""
        ...
