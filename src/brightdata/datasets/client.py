"""
Datasets client - main entry point for datasets API.
"""

from typing import List, Optional, TYPE_CHECKING

from .models import DatasetInfo
from .linkedin import LinkedInPeopleProfiles, LinkedInCompanyProfiles
from .amazon import AmazonProducts
from .crunchbase import CrunchbaseCompanies
from .imdb import IMDBMovies
from .nba import NBAPlayersStats
from .goodreads import GoodreadsBooks
from .world_population import WorldPopulation

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
        self._amazon_products: Optional[AmazonProducts] = None
        self._crunchbase_companies: Optional[CrunchbaseCompanies] = None
        self._imdb_movies: Optional[IMDBMovies] = None
        self._nba_players_stats: Optional[NBAPlayersStats] = None
        self._goodreads_books: Optional[GoodreadsBooks] = None
        self._world_population: Optional[WorldPopulation] = None

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
    def amazon_products(self) -> AmazonProducts:
        """Amazon Products dataset."""
        if self._amazon_products is None:
            self._amazon_products = AmazonProducts(self._engine)
        return self._amazon_products

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
