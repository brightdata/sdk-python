"""
Setup script for Bright Data SDK

This file provides backward compatibility for tools that don't support pyproject.toml.
The main configuration is in pyproject.toml following modern Python packaging standards.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from __init__.py
def read_version():
    try:
        with open(os.path.join("src", "brightdata", "__init__.py"), "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    except FileNotFoundError:
        return "0.1.0"
    return "0.1.0"

setup(
    name="brightdata-sdk",
    version=read_version(),
    author="Bright Data",
    author_email="support@brightdata.com",
    description="Python SDK for Bright Data Web Scraping and SERP APIs",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/brightdata/brightdata-sdk-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.9.0",
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.8.0",
        ],
    },
    keywords="brightdata, web scraping, proxy, serp, api, data extraction, aiohttp, bs4, openai",
    project_urls={
        "Bug Reports": "https://github.com/brightdata/brightdata-sdk-python/issues",
        "Documentation": "https://github.com/brightdata/brightdata-sdk-python#readme",
        "Source": "https://github.com/brightdata/brightdata-sdk-python",
    },
)
