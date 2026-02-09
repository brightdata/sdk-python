"""
Bright Data Datasets API client.

Access pre-collected datasets and filter records.
"""

from .client import DatasetsClient
from .base import BaseDataset, DatasetError
from .models import DatasetInfo, DatasetField, DatasetMetadata, SnapshotStatus
from .utils import export, export_json, export_jsonl, export_csv

# Platform-specific datasets
from .linkedin import LinkedInPeopleProfiles, LinkedInCompanyProfiles
from .amazon import AmazonProducts
from .crunchbase import CrunchbaseCompanies
from .imdb import IMDBMovies
from .nba import NBAPlayersStats
from .goodreads import GoodreadsBooks
from .world_population import WorldPopulation

__all__ = [
    # Client
    "DatasetsClient",
    # Base
    "BaseDataset",
    "DatasetError",
    # Models
    "DatasetInfo",
    "DatasetField",
    "DatasetMetadata",
    "SnapshotStatus",
    # Utils
    "export",
    "export_json",
    "export_jsonl",
    "export_csv",
    # LinkedIn
    "LinkedInPeopleProfiles",
    "LinkedInCompanyProfiles",
    # Amazon
    "AmazonProducts",
    # Crunchbase
    "CrunchbaseCompanies",
    # IMDB
    "IMDBMovies",
    # NBA
    "NBAPlayersStats",
    # Goodreads
    "GoodreadsBooks",
    # World Population
    "WorldPopulation",
]
