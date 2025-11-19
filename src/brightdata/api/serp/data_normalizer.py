"""Data normalization for SERP responses."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ...types import NormalizedSERPData


class BaseDataNormalizer(ABC):
    """Base class for SERP data normalization."""
    
    @abstractmethod
    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize SERP data to consistent format."""
        pass


class GoogleDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Google SERP responses."""
    
    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Google SERP data."""
        if not isinstance(data, (dict, str)):
            return {"results": []}
        
        if isinstance(data, str):
            return {
                "results": [],
                "raw_html": data,
            }
        
        results = []
        organic = data.get("organic", [])
        
        for i, item in enumerate(organic, 1):
            results.append({
                "position": i,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "displayed_url": item.get("displayed_url", ""),
            })
        
        normalized: NormalizedSERPData = {
            "results": results,
            "total_results": data.get("total_results"),
            "search_info": data.get("search_information", {}),
        }
        
        if "featured_snippet" in data:
            normalized["featured_snippet"] = data["featured_snippet"]
        
        if "knowledge_panel" in data:
            normalized["knowledge_panel"] = data["knowledge_panel"]
        
        if "people_also_ask" in data:
            normalized["people_also_ask"] = data["people_also_ask"]
        
        if "related_searches" in data:
            normalized["related_searches"] = data["related_searches"]
        
        if "ads" in data:
            normalized["ads"] = data["ads"]
        
        return normalized


class BingDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Bing SERP responses."""
    
    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Bing SERP data."""
        if isinstance(data, dict):
            return data
        return {"results": data if isinstance(data, list) else []}


class YandexDataNormalizer(BaseDataNormalizer):
    """Data normalizer for Yandex SERP responses."""
    
    def normalize(self, data: Any) -> NormalizedSERPData:
        """Normalize Yandex SERP data."""
        if isinstance(data, dict):
            return data
        return {"results": data if isinstance(data, list) else []}

