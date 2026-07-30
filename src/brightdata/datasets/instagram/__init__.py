"""Instagram datasets."""

from .comments import InstagramComments
from .posts import InstagramPosts
from .profiles import InstagramProfiles
from .reels import InstagramReels

__all__ = [
    "InstagramProfiles",
    "InstagramPosts",
    "InstagramComments",
    "InstagramReels",
]
