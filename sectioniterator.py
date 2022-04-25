from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scrapper import Scrapper
from typing import Any,Dict, Iterator, Optional
import logging

FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    # Logger is already configured, remove all handlers
    logger.handlers = []
logger.setLevel(logging.DEBUG)

class SectionIterator(Iterator):
    """Iterator for the 'sections' responses."""
    def __init__(self,
                 scrapper: Scrapper,
                 sections_extractor,
                 query_path: str,
                 first_data: Optional[Dict[str, Any]] = None,
                 post_type = None):
        self._scrapper = scrapper
        self.logger = scrapper.logger
        self._sections_extractor = sections_extractor
        self._query_path = query_path
        self.first_data = first_data
        self._data = self._query()
        self.next_page = 0
        self._page_index = 0
        self._section_index = 0
        self.post_type = post_type
        self.url_type = "tags"
    def __iter__(self):
        return self

    def _first(self):

        self.first_data = True
        res = self._scrapper.get_json(self._query_path, params={"__a": 1})
        self.next_page = 1 if res.get("next_page") is None else res.get("next_page")
        return self._sections_extractor(res)

    def _query(self, max_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.first_data:
            logger.info("_first")
            return self._first()
        """
        method : POST
        host: https://i.instagram.com
        path: api/v1/tags/{hashtag_name}/sections
        data : {"include_persistent": 0, "page": self.next_page, "surface": "grid", "tab": self.post_type, "next_page": Optional[None], "next_max_id: Optional[None]}
        """
        self._sections_extractor = lambda d: d["data"]
        data = {"include_persistent": 0,
                "page": self.next_page,
                "surface": "grid",
                "tab": self.post_type}

        pagination_variables = {"max_id": max_id, "next_page": self.next_page}
        res = self._scrapper.get_json(
            host="i.instagram.com",
            path=f"api/v1/{self.url_type}/{self._scrapper.hashtag_name}",
            params={"include_persistent": 0, "post": True, "data": data, **pagination_variables})


        self.next_page = res.get("next_page")
        return self._sections_extractor(res)

    def __next__(self):
        """
        when page index is smaller than section total number and section index < media of iteration,
        we have to add 1 to the section index

        when section index > media number
        we have to add 1 to the page index and make section index zero
        """
        if self._page_index < len(self._data['sections']):
            is_media_grid = self._data['sections'][self._page_index]['layout_type'] == "media_grid"
            if not is_media_grid:
                self._page_index += 1
                return None
            media = self._data['sections'][self._page_index]['layout_content']['medias'][self._section_index]['media']
            self._section_index += 1
            if self._section_index >= len(self._data['sections'][self._page_index]['layout_content']['medias']):
                self._section_index = 0
                self._page_index += 1
            return media
        if self._data['more_available']:
            self._page_index, self._section_index, self._data = 0, 0, self._query(self._data["next_max_id"])
            return self.__next__()
        raise StopIteration()
