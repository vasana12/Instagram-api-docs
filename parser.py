import logging
import re
import unicodedata
from contextlib import suppress
from typing import Dict, Any, Optional, List, Tuple
from urllib import request

from exceptions import InstabotException
from datetime import datetime

class Post:
    pass

class Parser:
    def __init__(self, raw=None, session=None):
        self.raw = raw
        pass

    def parse_hashtag(self, raw):
        pass

    def parse_hashtag_top_posts(self, raw):
        pass

    def parse_hashtag_recent_posts(self, raw):
        pass

    def parse_user(self, raw):
        pass

    def parse_user_posts(self, raw):
        pass

    def parse_user_followers(self, raw):
        pass

    def parse_user_followees(self, raw):
        pass

    def parse_post_details(self, raw):
        pass

    def _metadata(self, *keys) -> Any:
        try:
            d = self.raw
            for key in keys:
                d = d[key]
            return d
        except KeyError:
            return None

class Post:
    """
    Structure containing information about an Instagram post.
    """
    def __init__(self, raw: Dict[str, Any], search_type = None):
        assert 'shortcode' in raw or 'code' in raw
        FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger(__name__)
        if logger.hasHandlers():
            # Logger is already configured, remove all handlers
            logger.handlers = []
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        self.search_type = search_type
        self.raw = raw

        self._full_metadata_dict = None  # type: Optional[Dict[str, Any]]
        self._location = None            # type:
        self._iphone_struct_ = None

        if 'iphone_struct' in raw:
            self._iphone_struct_ = raw['iphone_struct']



    @property
    def shortcode(self) -> str:
        """Media shortcode. URL of the post is instagram.com/p/<shortcode>/."""
        return self.raw['shortcode'] if 'shortcode' in self.raw else self.raw['code']

    @property
    def clean_url(self) -> str:
        default_url = "https://www.instagram.com/p"
        return f"{default_url}/{self.shortcode}/"

    @property
    def mediaid(self) -> int:
        """The mediaid is a decimal representation of the media shortcode."""
        return int(self.raw['id'])

    @property
    def title(self) -> Optional[str]:
        """Title of post"""
        try:
            return self._field('title')
        except KeyError:
            return None






    @property
    def user(self):
        """user_info"""
        if self._iphone_struct_ is None:
            if "caption" in self.raw and self.raw["caption"] is not None:
                try:
                    return self.raw["caption"]["user"]
                except:

                    return None
            elif "user" in self.raw:
                try:
                    return self.raw["user"]
                except:

                    return None
            return None

        if "caption" in self._iphone_struct_ and self._iphone_struct_["caption"] is not None:
            try:
                return self._iphone_struct_["caption"]["user"]
            except:
                return None
        elif "user" in self._iphone_struct_:
            try:
                return self._iphone_struct_["user"]
            except:
                return None
        return None

    @property
    def profile_pic_url(self):
        return self.user["profile_pic_url"]



    @property
    def date_utc(self):
        try:
            return datetime.utcfromtimestamp(self.raw["taken_at"])
        except:
            return None

    @property
    def date(self) -> datetime:
        """Synonym to :attr:`~Post.date_utc`"""
        return self.date_utc


    @property
    def url(self):
        return self.raw[0]['url']


    def _field(self, *keys) -> Any:
        """Lookups given fields in _node, and if not found in _full_metadata. Raises KeyError if not found anywhere."""
        try:
            d = self.raw
            for key in keys:
                d = d[key]
            return d
        except KeyError:
            return None

    @property
    def typename(self) -> str:
        """Type of post, GraphImage, GraphVideo or GraphSidecar"""
        return self._field('__typename')

    @property
    def mediacount(self):
        """
        The number of media in a sidecar Post, or 1 if the Post it not a sidecar.
        """
        try:
            edges = self._field('edge_sidecar_to_children', 'edges')
            return edges
        except:
            return None



    def get_is_videos(self) -> List[bool]:
        """
        Return a list containing the ``is_video`` property for each media in the post.4.7
        """
        if self.typename == 'GraphSidecar':
            edges = self._field('edge_sidecar_to_children', 'edges')
            return [edge['node']['is_video'] for edge in edges]
        return [self.is_video]



    @property
    def caption(self) -> Optional[str]:
        if not self._iphone_struct_:
            if self.search_type != 'user':
                if "caption" in self.raw and self.raw["caption"] is not None:
                    try:
                        caption = self.raw["caption"]["text"]
                        caption = caption.replace("\n", "")
                        caption = re.sub("\s+", " ", caption)
                        caption = unicodedata.normalize('NFC', caption)
                        return caption
                    except:
                        return None
                return None

            else:
                if "edge_media_to_caption" in self.raw and self.raw["edge_media_to_caption"]["edges"]:
                    try:
                        caption = self.raw['edge_media_to_caption']['edges'][0]['node']['text']
                        caption = caption.replace("\n", "")
                        caption = re.sub("\s+", " ", caption)
                        return caption
                    except:
                        return None
                elif "caption" in self.raw:
                    try:
                        caption = self.raw["caption"]["text"]
                        caption = caption.replace("\n", "")
                        caption = re.sub("\s+", " ", caption)
                        return caption
                    except:
                        return None
                return None
        """Caption."""
        caption:str = ""
        self.logger.info(self.raw)
        if "edge_media_to_caption" in self.raw and self.raw["edge_media_to_caption"]["edges"]:
            caption = self.raw["edge_media_to_caption"]["edges"][0]["node"]["text"]
        elif "caption" in self.raw:
            caption = self.raw["caption"]
        try:
            caption = caption.replace("\n", "")
            caption = re.sub("\s+", " ", caption)
            caption = unicodedata.normalize('NFC', caption)
        except:
            return None
        return caption

    @property
    def caption_hashtags(self) -> Optional[str]:
        """List of all lowercased hashtags (without preceeding #) that occur in the Post's caption."""
        if not self.caption:
            return None
        hashtag_regex = re.compile(r"(?:#)(\w(?:(?:\w|(?:\.(?!\.))){0,28}(?:\w))?)")
        hashtag_list = re.findall(hashtag_regex, self.caption.lower())
        hashtag_list = list(map(lambda hashtag: "#"+ hashtag ,hashtag_list))
        return ",".join(hashtag_list)

    @property
    def caption_mentions(self) -> List[str]:
        """List of all lowercased profiles that are mentioned in the Post's caption, without preceeding @."""
        if not self.caption:
            return []
        mention_regex = re.compile(r"(?:^|\W|_)(?:@)(\w(?:(?:\w|(?:\.(?!\.))){0,28}(?:\w))?)")
        return re.findall(mention_regex, self.caption.lower())

    @property
    def tagged_users(self) -> List[str]:
        """List of all lowercased users that are tagged in the Post."""
        try:
            return [edge['node']['user']['username'].lower() for edge in self._field('edge_media_to_tagged_user',
                                                                                     'edges')]
        except KeyError:
            return []

    @property
    def is_video(self) -> bool:
        """True if the Post is a video."""
        return self.raw['is_video']


    @property
    def video_view_count(self) -> Optional[int]:
        """View count of the video, or None."""
        if self.is_video:
            return self._field('video_view_count')
        return None

    @property
    def video_duration(self) -> Optional[float]:
        """Duration of the video in seconds, or None."""
        if self.is_video:
            return self._field('video_duration')
        return None



    @property
    def likes(self) -> int:
        if not self._iphone_struct_:
            if self.search_type != 'user':
                """Likes count"""
                if "like_count" in self.raw:
                    try:
                        return self.raw["like_count"]
                    except:
                        return 0
            else:
                if "edge_media_preview_like" in self.raw:
                    try:
                        return self._field('edge_media_preview_like', 'count')
                    except:
                        return 0
                return 0

        """Likes count"""
        try:
            if "like_count" in self._iphone_struct_.keys():
                return self._iphone_struct_.get('like_count')
            else:
                self.logger.debug(f"shortcode:{self.shortcode} like_count error return 0")
                return 0
        except Exception as e:
            self.logger.debug(f"shortcode:{self.shortcode} like_count error")
            pass
        return self._field('edge_media_preview_like', 'count')

    @property
    def comments(self) -> int:
        """Comment count including answers"""
        if not self._iphone_struct_:
            if self.search_type != "user":
                """Comment count including answers"""
                try:
                    return self.raw["comment_count"]
                except KeyError:
                    return 0
            else:
                """Comment count including answers"""
                # If the count is already present in `self._node`, do not use `self._field` which could trigger fetching the
                # full metadata dict.
                comments = self.raw.get('edge_media_to_comment')
                if comments and 'count' in comments:
                    return comments['count']
                try:
                    return self._field('edge_media_to_parent_comment', 'count')
                except KeyError:
                    return self._field('edge_media_to_comment', 'count')
        try:
            if "comment_count" in self._iphone_struct_.keys():
                return self._iphone_struct_.get('comment_count')
            else:
                self.logger.error(f"shortcode:{self.shortcode} comments error return 0")
                return 0
        except Exception as e:
            self.logger.error(f"shortcode:{self.shortcode} comments error")
            pass

    @property
    def is_sponsored(self) -> bool:
        """
        Whether Post is a sponsored post, equivalent to non-empty :meth:`Post.sponsor_users`."""
        try:
            sponsor_edges = self._field('edge_media_to_sponsor_user', 'edges')
        except KeyError:
            return False
        return bool(sponsor_edges)

    @property
    def location(self) -> Optional[Dict]:
        try:
            location = self.raw["location"]
            return location
        except:
            return None

class User:
    def __init__(self, raw):
        pass

class Hashtag:
    def __init__(self, raw):
        pass
