from __future__ import annotations

import re
import time
from .exceptions import ValidationError, APIError
from typing import Any, Dict, List, Optional, Union


class SearchGPTResult:
    """
    Wrapper for GPT search results.

    Args
    
    raw : Any - The raw API response object (dict / list / text).
    text : str (property) - Best-effort extraction of the final answer text (T1).
    prompt : Optional[str] - The original prompt (for single result).
    country : Optional[str] - Country code used for the request (single result).
    usage : Optional[Dict[str, Any]] - Token/usage metadata if available.
    snapshot_id : Optional[str] - Present when sync=False (async job queued).
    """

    def __init__(
        self,
        raw: Any,
        prompt: Optional[str] = None,
        country: Optional[str] = None,
        usage: Optional[Dict[str, Any]] = None,
        snapshot_id: Optional[str] = None,
    ) -> None:
        self.raw = raw
        self.prompt = prompt
        self.country = country
        self.usage = usage
        self.snapshot_id = snapshot_id

    # helpers 
    @staticmethod
    def _coalesce(*vals) -> Optional[str]:
        for v in vals:
            if isinstance(v, str) and v.strip():
                return v
        return None

    @staticmethod
    def _dig(d: Any, *keys) -> Any:
        cur = d
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return None
        return cur

    @property
    def text(self) -> Optional[str]:
        """
        Best-effort extraction of ONLY the final answer text.
        Tries common fields/paths seen in ChatGPT-like payloads.
        Returns None if not found.
        """
        raw = self.raw

        # If API returned a plain string
        if isinstance(raw, str):
            return raw.strip() or None

        t = self._dig(raw, "answer")
        if isinstance(t, str):
            return t.strip() or None

        t = self._dig(raw, "data", "answer")
        if isinstance(t, str):
            return t.strip() or None

        t = self._dig(raw, "message", "content")
        if isinstance(t, str):
            return t.strip() or None

        choices = self._dig(raw, "choices")
        if isinstance(choices, list) and choices:
            content = self._dig(choices[0], "message", "content")
            if isinstance(content, str):
                return content.strip() or None
            
            content = choices[0].get("text") if isinstance(choices[0], dict) else None
            if isinstance(content, str):
                return content.strip() or None

        t = self._dig(raw, "result")
        if isinstance(t, str):
            return t.strip() or None
        t = self._dig(raw, "output")
        if isinstance(t, str):
            return t.strip() or None

        for key in ("content", "text", "final", "final_text"):
            v = self._dig(raw, key)
            if isinstance(v, str):
                return v.strip() or None

        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "country": self.country,
            "usage": self.usage,
            "snapshot_id": self.snapshot_id,
            "raw": self.raw,
            "text": self.text,
        }


class Search:
    """
    Namespaced search interface.
    """

    def __init__(self, client) -> None:
        self._c = client  # root client (reuses session, APIs, zones)

    def __call__(
        self,
        query: Union[str, List[str]],
        search_engine: str = "google",
        zone: str = None,
        response_format: str = "raw",
        method: str = "GET",
        country: str = "",
        data_format: str = "html",
        async_request: bool = False,
        max_workers: int = None,
        timeout: int = None,
        parse: bool = False,
    ):
        return self.web(
            query=query,
            search_engine=search_engine,
            zone=zone,
            response_format=response_format,
            method=method,
            country=country,
            data_format=data_format,
            async_request=async_request,
            max_workers=max_workers,
            timeout=timeout,
            parse=parse,
        )

    # GPT 
    def gpt(
        self,
        prompt: Union[str, List[str]],
        country: Union[str, List[str]] = None,
        secondary_prompt: Union[str, List[str]] = None,
        web_search: Union[bool, List[bool]] = False,
        sync: bool = True,
        timeout: int = None,
    ) -> Union[SearchGPTResult, List[SearchGPTResult]]:
        """
        Query ChatGPT via Bright Data's dataset API.

        Returns - Single object for single prompt, list for multiple prompts (M2).
        """
        prompts: List[str]
        if isinstance(prompt, str):
            prompts = [prompt]
        elif isinstance(prompt, list) and all(isinstance(p, str) for p in prompt):
            prompts = prompt
        else:
            raise ValidationError("Invalid prompt input: must be a non-empty string or list of strings.")
        if not prompts:
            raise ValidationError("At least one prompt is required.")

        # normalization helper 
        def _norm(param, name):
            if param is None:
                return [None] * len(prompts)
            if isinstance(param, list):
                if len(param) != len(prompts):
                    raise ValidationError(f"{name} list must have the same length as prompts.")
                return param
            return [param] * len(prompts)

        countries = _norm(country, "country")
        secondary_prompts = _norm(secondary_prompt, "secondary_prompt")
        web_searches = _norm(web_search, "web_search")

        # validation
        for c in countries:
            if c and not re.match(r"^[A-Z]{2}$", c):
                raise ValidationError(f"Invalid country code '{c}'. Must be 2 uppercase letters.")
        for s in secondary_prompts:
            if s is not None and not isinstance(s, str):
                raise ValidationError("Secondary prompts must be strings.")
        for w in web_searches:
            if not isinstance(w, bool):
                raise ValidationError("Web search flags must be boolean.")
        if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
            raise ValidationError("Timeout must be a positive integer.")

        timeout = timeout or (65 if sync else 30)

        # retries around API call
        max_retries = 3
        last_err = None
        for attempt in range(max_retries):
            try:
                result = self._c.chatgpt_api.scrape_chatgpt(
                    prompts=prompts,
                    countries=countries,
                    additional_prompts=secondary_prompts,
                    web_searches=web_searches,
                    sync=sync,
                    timeout=timeout,
                )
                # Wrap result(s)
                if not sync:
                    # Async: expect {"snapshot_id": "...", ...}
                    snapshot_id = result.get("snapshot_id") if isinstance(result, dict) else None
                    return SearchGPTResult(raw=result, snapshot_id=snapshot_id)

                if isinstance(result, list):
                    out: List[SearchGPTResult] = []
                    if len(result) == len(prompts):
                        for i, item in enumerate(result):
                            out.append(
                                SearchGPTResult(
                                    raw=item,
                                    prompt=prompts[i],
                                    country=countries[i],
                                    usage=None,
                                )
                            )
                    else:
                        for item in result:
                            out.append(SearchGPTResult(raw=item))
                    return out[0] if len(prompts) == 1 and len(out) == 1 else out

                return SearchGPTResult(raw=result, prompt=prompts[0] if len(prompts) == 1 else None)

            except APIError as e:
                last_err = e
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise e
            except Exception as e:
                if isinstance(e, (ValidationError, APIError)):
                    raise
                last_err = e
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise APIError(f"Unexpected error in search.gpt: {e}") from e

        if last_err:
            raise last_err
        raise APIError("Unknown error in search.gpt")

    # Web (SERP)
    def web(
        self,
        query: Union[str, List[str]],
        search_engine: str = "google",
        zone: str = None,
        response_format: str = "raw",
        method: str = "GET",
        country: str = "",
        data_format: str = "html",
        async_request: bool = False,
        max_workers: int = None,
        timeout: int = None,
        parse: bool = False,
    ):
        """
        Web/SERP search wrapper. Thin pass-through to SearchAPI with validation.
        """
        if not query:
            raise ValueError("The 'query' parameter cannot be None or empty.")
        if isinstance(query, str):
            if not query.strip():
                raise ValueError("The 'query' string cannot be empty or whitespace.")
        elif isinstance(query, list):
            if not all(isinstance(q, str) and q.strip() for q in query):
                raise ValueError("All queries in the list must be non-empty strings.")
        else:
            raise TypeError("The 'query' parameter must be a string or a list of strings.")

        zone = zone or self._c.serp_zone
        max_workers = max_workers or self._c.DEFAULT_MAX_WORKERS

        return self._c.search_api.search(
            query, search_engine, zone, response_format, method, country,
            data_format, async_request, max_workers, timeout, parse
        )

    # LinkedIn
    @property
    def linkedin(self):
        """
        Namespaced LinkedIn search helpers.
        """
        return self._c.search_linkedin
