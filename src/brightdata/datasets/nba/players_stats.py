"""
NBA Players Stats dataset.

Dataset ID: gd_lrqirmftwxxatiorf

See FIELDS dict for all filterable fields with descriptions.
"""

from typing import TYPE_CHECKING, Dict, Any

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class NBAPlayersStats(BaseDataset):
    """
    NBA Players Stats dataset.

    Access NBA player statistics with filtering.

    Example:
        >>> players = client.datasets.nba_players_stats
        >>> metadata = await players.get_metadata()
        >>> snapshot_id = await players.filter(
        ...     filter={"name": "player_points_per_game", "operator": ">", "value": 20},
        ...     records_limit=100
        ... )
        >>> data = await players.download(snapshot_id)
    """

    DATASET_ID = "gd_lrqirmftwxxatiorf"
    NAME = "nba_players_stats"

    # All available fields with metadata
    FIELDS: Dict[str, Dict[str, Any]] = {
        # Player identification
        "url": {
            "type": "url",
            "description": "ESPN player stats page URL",
        },
        "player_name": {
            "type": "text",
            "description": "Player full name",
        },
        "team": {
            "type": "text",
            "description": "Team abbreviation (e.g., LAL, GSW)",
        },
        # Season info
        "season_year": {
            "type": "text",
            "description": "Season year (e.g., 2024-25)",
        },
        "season_type": {
            "type": "text",
            "description": "Season type (Regular, Playoffs)",
        },
        # Games
        "player_games_played": {
            "type": "number",
            "description": "Number of games played",
        },
        "player_games_started": {
            "type": "number",
            "description": "Number of games started",
        },
        "player_minutes_per_game": {
            "type": "number",
            "description": "Minutes played per game",
        },
        # Scoring
        "player_points_per_game": {
            "type": "number",
            "description": "Points scored per game",
        },
        # Rebounds
        "player_offensive_rebounds_per_game": {
            "type": "number",
            "description": "Offensive rebounds per game",
        },
        "player_defensive_rebounds_per_game": {
            "type": "number",
            "description": "Defensive rebounds per game",
        },
        "player_rebounds_per_game": {
            "type": "number",
            "description": "Total rebounds per game",
        },
        # Assists & turnovers
        "player_assists_per_game": {
            "type": "number",
            "description": "Assists per game",
        },
        "player_turnovers_per_game": {
            "type": "number",
            "description": "Turnovers per game",
        },
        "player_assist_to_turnover_ratio": {
            "type": "number",
            "description": "Assist to turnover ratio",
        },
        # Defense
        "player_steals_per_game": {
            "type": "number",
            "description": "Steals per game",
        },
        "player_blocks_per_game": {
            "type": "number",
            "description": "Blocks per game",
        },
        # Fouls
        "player_fouls_per_game": {
            "type": "number",
            "description": "Personal fouls per game",
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
    def get_per_game_stats(cls) -> list:
        """Get all per-game statistics fields."""
        return [name for name in cls.FIELDS.keys() if "per_game" in name.lower()]
