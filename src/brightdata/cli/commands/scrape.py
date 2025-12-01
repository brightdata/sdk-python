"""
CLI commands for scraping operations (URL-based extraction).
"""

import click
from typing import Optional

from ..utils import create_client, output_result, handle_error


@click.group("scrape")
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
def scrape_group(
    ctx: click.Context, api_key: Optional[str], output_format: str, output_file: Optional[str]
) -> None:
    """
    Scrape operations - URL-based data extraction.

    Extract data from specific URLs using specialized scrapers.
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["output_format"] = output_format
    ctx.obj["output_file"] = output_file


# ============================================================================
# Generic Scraper
# ============================================================================


@scrape_group.command("generic")
@click.argument("url", required=True)
@click.option("--country", default="", help="Country code for targeting")
@click.option("--response-format", default="raw", help="Response format (raw, json)")
@click.pass_context
def scrape_generic(ctx: click.Context, url: str, country: str, response_format: str) -> None:
    """Scrape any URL using generic web scraper."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.generic.url(
            url=url, country=country, response_format=response_format
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# Amazon Scraper
# ============================================================================


@scrape_group.group("amazon")
def amazon_group() -> None:
    """Amazon scraping operations."""
    pass


@amazon_group.command("products")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def amazon_products(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Amazon product data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.amazon.products(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@amazon_group.command("reviews")
@click.argument("url", required=True)
@click.option("--past-days", type=int, help="Number of past days to consider")
@click.option("--keyword", help="Filter reviews by keyword")
@click.option("--num-reviews", type=int, help="Number of reviews to scrape")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def amazon_reviews(
    ctx: click.Context,
    url: str,
    past_days: Optional[int],
    keyword: Optional[str],
    num_reviews: Optional[int],
    timeout: int,
) -> None:
    """Scrape Amazon product reviews from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.amazon.reviews(
            url=url, pastDays=past_days, keyWord=keyword, numOfReviews=num_reviews, timeout=timeout
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@amazon_group.command("sellers")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def amazon_sellers(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Amazon seller data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.amazon.sellers(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# LinkedIn Scraper
# ============================================================================


@scrape_group.group("linkedin")
def linkedin_group() -> None:
    """LinkedIn scraping operations."""
    pass


@linkedin_group.command("profiles")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_profiles(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape LinkedIn profile data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.linkedin.profiles(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@linkedin_group.command("posts")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_posts(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape LinkedIn post data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.linkedin.posts(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@linkedin_group.command("jobs")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_jobs(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape LinkedIn job data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.linkedin.jobs(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@linkedin_group.command("companies")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=180, help="Timeout in seconds")
@click.pass_context
def linkedin_companies(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape LinkedIn company data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.linkedin.companies(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# Facebook Scraper
# ============================================================================


@scrape_group.group("facebook")
def facebook_group() -> None:
    """Facebook scraping operations."""
    pass


@facebook_group.command("posts-by-profile")
@click.argument("url", required=True)
@click.option("--num-posts", type=int, help="Number of posts to collect")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def facebook_posts_by_profile(
    ctx: click.Context,
    url: str,
    num_posts: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Scrape Facebook posts from profile URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.facebook.posts_by_profile(
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


@facebook_group.command("posts-by-group")
@click.argument("url", required=True)
@click.option("--num-posts", type=int, help="Number of posts to collect")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def facebook_posts_by_group(
    ctx: click.Context,
    url: str,
    num_posts: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Scrape Facebook posts from group URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.facebook.posts_by_group(
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


@facebook_group.command("posts-by-url")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def facebook_posts_by_url(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Facebook post data from post URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.facebook.posts_by_url(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@facebook_group.command("comments")
@click.argument("url", required=True)
@click.option("--num-comments", type=int, help="Number of comments to collect")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def facebook_comments(
    ctx: click.Context,
    url: str,
    num_comments: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Scrape Facebook comments from post URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.facebook.comments(
            url=url,
            num_of_comments=num_comments,
            start_date=start_date,
            end_date=end_date,
            timeout=timeout,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@facebook_group.command("reels")
@click.argument("url", required=True)
@click.option("--num-posts", type=int, help="Number of reels to collect")
@click.option("--start-date", help="Start date (MM-DD-YYYY)")
@click.option("--end-date", help="End date (MM-DD-YYYY)")
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def facebook_reels(
    ctx: click.Context,
    url: str,
    num_posts: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    timeout: int,
) -> None:
    """Scrape Facebook reels from profile URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.facebook.reels(
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


# ============================================================================
# Instagram Scraper
# ============================================================================


@scrape_group.group("instagram")
def instagram_group() -> None:
    """Instagram scraping operations."""
    pass


@instagram_group.command("profiles")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_profiles(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Instagram profile data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.instagram.profiles(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@instagram_group.command("posts")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_posts(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Instagram post data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.instagram.posts(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@instagram_group.command("comments")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_comments(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Instagram comments from post URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.instagram.comments(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


@instagram_group.command("reels")
@click.argument("url", required=True)
@click.option("--timeout", type=int, default=240, help="Timeout in seconds")
@click.pass_context
def instagram_reels(ctx: click.Context, url: str, timeout: int) -> None:
    """Scrape Instagram reel data from URL."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.instagram.reels(url=url, timeout=timeout)
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()


# ============================================================================
# ChatGPT Scraper
# ============================================================================


@scrape_group.group("chatgpt")
def chatgpt_group() -> None:
    """ChatGPT scraping operations."""
    pass


@chatgpt_group.command("prompt")
@click.argument("prompt", required=True)
@click.option("--country", default="us", help="Country code")
@click.option("--web-search", is_flag=True, help="Enable web search")
@click.option("--additional-prompt", help="Follow-up prompt")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds")
@click.pass_context
def chatgpt_prompt(
    ctx: click.Context,
    prompt: str,
    country: str,
    web_search: bool,
    additional_prompt: Optional[str],
    timeout: int,
) -> None:
    """Send a prompt to ChatGPT."""
    try:
        client = create_client(ctx.obj["api_key"])
        result = client.scrape.chatgpt.prompt(
            prompt=prompt,
            country=country,
            web_search=web_search,
            additional_prompt=additional_prompt,
        )
        output_result(result, ctx.obj["output_format"], ctx.obj["output_file"])
    except Exception as e:
        handle_error(e)
        raise click.Abort()
