"""
CLI commands for search operations (parameter-based discovery).
"""

import click
from typing import Optional

from ..utils import create_client, output_result, handle_error


@click.group("search")
@click.option(
    "--api-key",
    envvar="BRIGHTDATA_API_TOKEN",
    help="Bright Data API key (or set BRIGHTDATA_API_TOKEN env var)",
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "pretty", "minimal"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option("--output-file", type=click.Path(), help="Save output to file")
@click.pass_context
def search_group(
    ctx: click.Context, api_key: Optional[str], output_format: str, output_file: Optional[str]
) -> None:
    """
    Search operations - Parameter-based discovery.

    Discover data using search parameters rather than specific URLs.
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["output_format"] = output_format
    ctx.obj["output_file"] = output_file


# ============================================================================
# SERP Services (Google, Bing, Yandex)
# ============================================================================


@search_group.command("google")
@click.argument("query", required=True)
@click.option("--location", help="Geographic location (e.g., 'United States', 'New York')")
@click.option("--language", default="en", help="Language code (e.g., 'en', 'es', 'fr')")
@click.option(
    "--device",
    default="desktop",
    type=click.Choice(["desktop", "mobile", "tablet"]),
    help="Device type",
)
@click.option("--num-results", type=int, default=10, help="Number of results to return")
@click.pass_context
def search_google(
    ctx: click.Context,
    query: str,
    location: Optional[str],
    language: str,
    device: str,
    num_results: int,
) -> None:
    """Search Google and get results."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.google(
            query=query,
            location=location,
            language=language,
            device=device,
            num_results=num_results,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@search_group.command("bing")
@click.argument("query", required=True)
@click.option("--location", help="Geographic location")
@click.option("--language", default="en", help="Language code")
@click.option("--num-results", type=int, default=10, help="Number of results to return")
@click.pass_context
def search_bing(
    ctx: click.Context, query: str, location: Optional[str], language: str, num_results: int
) -> None:
    """Search Bing and get results."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.bing(
            query=query, location=location, language=language, num_results=num_results
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@search_group.command("yandex")
@click.argument("query", required=True)
@click.option("--location", help="Geographic location")
@click.option("--language", default="ru", help="Language code")
@click.option("--num-results", type=int, default=10, help="Number of results to return")
@click.pass_context
def search_yandex(
    ctx: click.Context, query: str, location: Optional[str], language: str, num_results: int
) -> None:
    """Search Yandex and get results."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.yandex(
            query=query, location=location, language=language, num_results=num_results
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# LinkedIn Search
# ============================================================================


@search_group.group("linkedin")
def linkedin_search_group() -> None:
    """LinkedIn search operations."""
    pass


@linkedin_search_group.command("posts")
@click.argument("profile-url", required=True)
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--end-date", help="End date (YYYY-MM-DD)")
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_search_posts(
    ctx: click.Context,
    profile_url: str,
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Discover LinkedIn posts from profile within date range."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.linkedin.posts(
            profile_url=profile_url, start_date=start_date, end_date=end_date, timeout=timeout
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@linkedin_search_group.command("profiles")
@click.argument("first-name", required=True)
@click.option("--last-name", help="Last name")
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_search_profiles(
    ctx: click.Context, first_name: str, last_name: Optional[str], timeout: int
) -> None:
    """Find LinkedIn profiles by name."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.linkedin.profiles(
            firstName=first_name, lastName=last_name, timeout=timeout
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@linkedin_search_group.command("jobs")
@click.option("--url", help="Job URL (optional)")
@click.option("--keyword", help="Job keyword")
@click.option("--location", help="Job location")
@click.option("--country", help="Country code")
@click.option("--time-range", help="Time range filter")
@click.option("--job-type", help="Job type filter")
@click.option("--experience-level", help="Experience level filter")
@click.option("--remote", is_flag=True, help="Remote jobs only")
@click.option("--company", help="Company name filter")
@click.option("--location-radius", type=int, help="Location radius in miles")
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_search_jobs(
    ctx: click.Context,
    url: Optional[str],
    keyword: Optional[str],
    location: Optional[str],
    country: Optional[str],
    time_range: Optional[str],
    job_type: Optional[str],
    experience_level: Optional[str],
    remote: bool,
    company: Optional[str],
    location_radius: Optional[int],
    timeout: int,
) -> None:
    """Find LinkedIn jobs by criteria."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.linkedin.jobs(
            url=url,
            keyword=keyword,
            location=location,
            country=country,
            timeRange=time_range,
            jobType=job_type,
            experienceLevel=experience_level,
            remote=remote,
            company=company,
            locationRadius=location_radius,
            timeout=timeout,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# ChatGPT Search
# ============================================================================


@search_group.group("chatgpt")
def chatgpt_search_group() -> None:
    """ChatGPT search operations."""
    pass


@chatgpt_search_group.command("prompt")
@click.argument("prompt", required=True)
@click.option("--country", help="Country code (2-letter format)")
@click.option("--web-search", is_flag=True, help="Enable web search")
@click.option("--secondary-prompt", help="Secondary/follow-up prompt")
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def chatgpt_search_prompt(
    ctx: click.Context,
    prompt: str,
    country: Optional[str],
    web_search: bool,
    secondary_prompt: Optional[str],
    timeout: int,
) -> None:
    """Send a prompt to ChatGPT via search service."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.chatGPT.chatGPT(
            prompt=prompt,
            country=country,
            webSearch=web_search if web_search else None,
            secondaryPrompt=secondary_prompt,
            timeout=timeout,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# Instagram Search
# ============================================================================


@search_group.group("instagram")
def instagram_search_group() -> None:
    """Instagram search operations."""
    pass


@instagram_search_group.command("posts")
@click.argument("url", required=True)
@click.option("--num-posts", type=int, help="Number of posts to discover")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--post-type", help="Post type filter")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_search_posts(
    ctx: click.Context,
    url: str,
    num_posts: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    post_type: Optional[str],
    timeout: int,
) -> None:
    """Discover Instagram posts from profile."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.instagram.posts(
            url=url,
            num_of_posts=num_posts,
            start_date=start_date,
            end_date=end_date,
            post_type=post_type,
            timeout=timeout,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@instagram_search_group.command("reels")
@click.argument("url", required=True)
@click.option("--num-posts", type=int, help="Number of reels to discover")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_search_reels(
    ctx: click.Context,
    url: str,
    num_posts: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Discover Instagram reels from profile."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.search.instagram.reels(
            url=url,
            num_of_posts=num_posts,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()
