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


# Read version from src/brightdata/__init__.py (src layout)
def read_version():
    version_file = os.path.join("src", "brightdata", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    # Fallback to _version.py
    version_file = os.path.join("src", "brightdata", "_version.py")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("__version__"):
                    return line.split('"')[1]
    return "2.0.0"


setup(
    name="brightdata-sdk",
    version=read_version(),
    author="Bright Data",
    author_email="support@brightdata.com",
    description="Modern async-first Python SDK for Bright Data Web Scraping, SERP, and Platform APIs",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/brightdata/sdk-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "pandas>=1.5.0",
            "matplotlib>=3.5.0",
            "tqdm>=4.64.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "brightdata=brightdata.cli.main:main",
        ],
    },
    keywords="brightdata, web scraping, proxy, serp, api, data extraction, async, pandas, jupyter",
    project_urls={
        "Bug Reports": "https://github.com/brightdata/sdk-python/issues",
        "Documentation": "https://github.com/brightdata/sdk-python#readme",
        "Source": "https://github.com/brightdata/sdk-python",
        "Changelog": "https://github.com/brightdata/sdk-python/blob/main/CHANGELOG.md",
    },
)
