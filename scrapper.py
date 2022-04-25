import hashlib
import logging
import re
from datetime import datetime, timedelta
import json
import random
from typing import Optional, Dict, Any, List
import time
import requests

from exceptions import ConnectionException, QueryReturnedNotFoundException, \
    LoginRequiredException, TooManyRequestsException, QueryReturnedBadRequestException
from nodeiterator import NodeIterator
from sectioniterator import SectionIterator


class Scrapper:
    def __init__(self, session):
        self._session = session
        self.max_connection_attempts = 3
        self._rate_controller = RateController()
        self.hashtag_name = None
        self.username = session.username
        self._node = None

        FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger(__name__)
        if logger.hasHandlers():
            # Logger is already configured, remove all handlers
            logger.handlers = []
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        pass

    @property
    def is_logged_in(self) -> bool:
        """True, if this Instaloader instance is logged in."""
        return bool(self.username)

    def do_sleep(self):
        time.sleep(random.randint(0, 5))

    def get_hashtag(self, hashtag):
        """
        url : https://www.instagram.com
        path : explore/tags/{hashtag}
        params : {"__a" : 1}
        """
        self.hashtag_name = hashtag
        json_response = self.get_json(host="www.instagram.com", path=f"explore/tags/{hashtag}/", params={"__a": 1})
        self._node = json_response
        return json_response["graphql"]["hashtag"] if "graphql" in json_response else json_response["data"]

    def get_hashtag_top_posts(self, hashtag):
        """Yields the top posts of the hashtag."""
        yield from SectionIterator(
            self,
            lambda d: d["data"]["top"],
            f"explore/tags/{hashtag}/",
            None,
            post_type="top"
        )


    def get_hashtag_recent_posts(self, hashtag):
        """Yields the top posts of the hashtag."""
        yield from SectionIterator(
            self,
            lambda d: d["data"]["recent"],
            f"explore/tags/{hashtag}/",
            None,
            post_type="recent"
        )

    def get_user(self, username):
        """
        url : https://www.instagram.com
        path : {username}/feed
        params : {}
        """
        json_response = self.get_json(host="www.instagram.com", path=f"{username}/feed", params={})
        return json_response['entry_data']['ProfilePage'][0]['graphql']['user']
        pass

    def get_user_posts(self, userid):
        """Retrieve all posts from a profile.
        :rtype: NodeIterator[Post]"""
        return NodeIterator(
            self,
            '003056d32c2554def87228bc3fd9668a',
            lambda d: d['data']['user']['edge_owner_to_timeline_media'],
            {'id': userid},
            'https://www.instagram.com/{0}/'.format(self.username),
            first_data=None,
        )
        pass

    def get_user_followers(self,userid):
        """
        Retrieve list of followers of given userid.
        To use this, needs to be logged in and private profiles has to be followed.
        """
        return NodeIterator(
            self,
            '37479f2b8209594dde7facb0d904896a',
            lambda d: d['data']['user']['edge_followed_by'],
            {'id': userid},
            'https://www.instagram.com/{0}/'.format(self.username)
        )

    def get_user_followees(self, userid):
        """
        Retrieve list of followees of given userid.
        To use this, needs to be logged in and private profiles has to be followed.
        """
        return NodeIterator(
            self,
            '37479f2b8209594dde7facb0d904896a',
            lambda d: d['data']['user']['edge_follow'],
            {'id': userid},
            'https://www.instagram.com/{0}/'.format(self.username)
        )


    def get_post_details(self):
            pass

    def get_json(self, path: str, params: Dict[str, Any], host: str = 'www.instagram.com', _attempt = 1) -> Dict[str, Any]:
        """JSON request to Instagram.

        :param path: URL, relative to the given domain which defaults to www.instagram.com/
        :param params: GET parameters
        :param host: Domain part of the URL from where to download the requested JSON; defaults to www.instagram.com
        :param session: Session to use, self.session
        :return: Decoded response dictionary
        :raises QueryReturnedBadRequestException: When the server responds with a 400.
        :raises QueryReturnedNotFoundException: When the server responds with a 404.
        :raises ConnectionException: When query repeatedly failed.
        """
        is_graphql_query = 'query_hash' in params and 'graphql/query' in path
        is_iphone_query = host == 'i.instagram.com'
        is_other_query = not is_graphql_query and host == "www.instagram.com"

        try:
            self.do_sleep()
            if is_graphql_query:
                self._rate_controller.wait_before_query(params['query_hash'])
            if is_iphone_query:
                self._rate_controller.wait_before_query('iphone')
            if is_other_query:
                self._rate_controller.wait_before_query('other')

            is_post = "post" in params

            if is_post:
                data = params.get("data")
                self.logger.info(f'POST to endpoint - https://{host}/{path}/sections/')
                resp = self._session.post(f'https://{host}/{path}/sections/', data=data, allow_redirects=False)

            else:
                resp = self._session.get('https://{0}/{1}'.format(host, path), params=params, allow_redirects=False)

            while resp.is_redirect:
                redirect_url = resp.headers['location']
                self.logger.info('\nHTTP redirect from https://{0}/{1} to {2}'.format(host, path, redirect_url))
                if redirect_url.startswith('https://www.instagram.com/accounts/login'):
                    if not self.is_logged_in:
                        raise LoginRequiredException("Redirected to login page. Use --login.")
                    # alternate rate limit exceeded behavior
                    raise TooManyRequestsException("Redirected to login")
                if redirect_url.startswith('https://{}/'.format(host)):
                    resp = self._session.get(redirect_url if redirect_url.endswith('/') else redirect_url + '/',
                                    params=params, allow_redirects=False)
                else:
                    break

            ###다른 아이디로 로그인 해야함
            if resp.status_code == 400:
                raise QueryReturnedBadRequestException("400 Bad Request")
            if resp.status_code == 404:
                raise QueryReturnedNotFoundException("404 Not Found")
            if resp.status_code == 429:
                raise TooManyRequestsException("429 Too Many Requests")
            if resp.status_code != 200:
                raise ConnectionException("HTTP error code {}.".format(resp.status_code))

            is_html_query = not is_graphql_query and not "__a" in params and host == "www.instagram.com" and not is_post
            if is_html_query:
                match = re.search(r'window\._sharedData = (.*);</script>', resp.text)
                if match is None:
                    raise QueryReturnedNotFoundException("Could not find \"window._sharedData\" in html response.")
                resp_json = json.loads(match.group(1))
                entry_data = resp_json.get('entry_data')

                post_or_profile_page = list(entry_data.values())[0] if entry_data is not None else None
                if post_or_profile_page is None:
                    raise ConnectionException("\"window._sharedData\" does not contain required keys.")
                # If GraphQL data is missing in `window._sharedData`, search for it in `__additionalDataLoaded`.
                if 'graphql' not in post_or_profile_page[0]:
                    match = re.search(r'window\.__additionalDataLoaded\(.*?({.*"graphql":.*})\);</script>',
                                      resp.text)
                    if match is not None:
                        post_or_profile_page[0]['graphql'] = json.loads(match.group(1))['graphql']
                return resp_json
            else:
                resp_json = resp.json()
            if 'status' in resp_json and resp_json['status'] != "ok":
                if 'message' in resp_json:
                    raise ConnectionException("Returned \"{}\" status, message \"{}\".".format(resp_json['status'],
                                                                                               resp_json['message']))
                else:
                    raise ConnectionException("Returned \"{}\" status.".format(resp_json['status']))
            return resp_json if not is_post else {"data": resp_json}
        except (ConnectionException, json.decoder.JSONDecodeError, requests.exceptions.RequestException) as err:
            error_string = "JSON Query to {}: {}".format(path, err)
            if _attempt == self.max_connection_attempts:
                if isinstance(err, QueryReturnedNotFoundException):
                    raise QueryReturnedNotFoundException(error_string) from err
                else:
                    raise ConnectionException(error_string) from err
            self.logger.error(error_string + " [retrying; skip with ^C]")
            try:
                if isinstance(err, TooManyRequestsException):
                    if is_graphql_query:
                        self._rate_controller.handle_429(params['query_hash'])
                    if is_iphone_query:
                        self._rate_controller.handle_429('iphone')
                    if is_other_query:
                        self._rate_controller.handle_429('other')
                return self.get_json(host=host , path=path, params=params, _attempt=_attempt + 1)
            except KeyboardInterrupt:
                self.logger.error("[skipped by user]")
                raise ConnectionException(error_string) from err

    def graphql_query(self, query_hash: str, variables: Dict[str, Any], rhx_gis: Optional[str] = None) -> Dict[str, Any]:


        variables_json = json.dumps(variables, separators=(',', ':'))
        if rhx_gis:
            #self.log("rhx_gis {} query_hash {}".format(rhx_gis, query_hash))
            values = "{}:{}".format(rhx_gis, variables_json)
            x_instagram_gis = hashlib.md5(values.encode()).hexdigest()
            self._session.headers['x-instagram-gis'] = x_instagram_gis

        resp_json = self.get_json('graphql/query',
                                  params={'query_hash': query_hash,
                                          'variables': variables_json})
        if 'status' not in resp_json:
            self.logger.error("GraphQL response did not contain a \"status\" field.")
        return resp_json

class RateController:
    def __init__(self):
        self._query_timestamps = dict()  # type: Dict[str, List[float]]
        self._earliest_next_request_time = 0.0
        self._iphone_earliest_next_request_time = 0.0
        FORMAT = '%(module)s.%(funcName)s - %(message)s - %(levelname)s - %(asctime)s'
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger(__name__)
        if logger.hasHandlers():
            # Logger is already configured, remove all handlers
            logger.handlers = []
        logger.setLevel(logging.INFO)
        self.logger = logger
    def sleep(self, secs: float):
        """Wait given number of seconds."""
        # Not static, to allow for the behavior of this method to depend on context-inherent properties, such as
        # whether we are logged in.
        # pylint:disable=no-self-use
        time.sleep(secs)

    def _dump_query_timestamps(self, current_time: float, failed_query_type: str):
        windows = [10, 11, 20, 22, 30, 60]
        self.logger.error(f"Number of requests within last {'/'.join(str(w) for w in windows)} minutes grouped by type:")
        for query_type, times in self._query_timestamps.items():
            reqs_in_sliding_window = [sum(t > current_time - w * 60 for t in times) for w in windows]
            self.logger.error(" {} {:>32}: {}".format("*" if query_type == failed_query_type else " ", query_type, " ".join("{:4}".format(reqs) for reqs in reqs_in_sliding_window)))

    def count_per_sliding_window(self, query_type: str) -> int:

        return 75 if query_type == 'other' else 200

    def _reqs_in_sliding_window(self, query_type: Optional[str], current_time: float, window: float) -> List[float]:
        if query_type is not None:
            # timestamps of type query_type
            relevant_timestamps = self._query_timestamps[query_type]
        else:
            # all GraphQL queries, i.e. not 'iphone' or 'other'
            graphql_query_timestamps = filter(lambda tp: tp[0] not in ['iphone', 'other'],
                                              self._query_timestamps.items())
            relevant_timestamps = [t for times in (tp[1] for tp in graphql_query_timestamps) for t in times]
        return list(filter(lambda t: t > current_time - window, relevant_timestamps))

    def query_waittime(self, query_type: str, current_time: float, untracked_queries: bool = False) -> float:
        """Calculate time needed to wait before query can be executed."""
        per_type_sliding_window = 660
        iphone_sliding_window = 1800
        if query_type not in self._query_timestamps:
            self._query_timestamps[query_type] = []
        self._query_timestamps[query_type] = list(filter(lambda t: t > current_time - 60 * 60,
                                                         self._query_timestamps[query_type]))

        def per_type_next_request_time():
            reqs_in_sliding_window = self._reqs_in_sliding_window(query_type, current_time, per_type_sliding_window)
            if len(reqs_in_sliding_window) < self.count_per_sliding_window(query_type):
                return 0.0
            else:
                return min(reqs_in_sliding_window) + per_type_sliding_window + 6

        def gql_accumulated_next_request_time():
            if query_type in ['iphone', 'other']:
                return 0.0
            gql_accumulated_sliding_window = 600
            gql_accumulated_max_count = 275
            reqs_in_sliding_window = self._reqs_in_sliding_window(None, current_time, gql_accumulated_sliding_window)
            if len(reqs_in_sliding_window) < gql_accumulated_max_count:
                return 0.0
            else:
                return min(reqs_in_sliding_window) + gql_accumulated_sliding_window

        def untracked_next_request_time():
            if untracked_queries:
                if query_type == "iphone":
                    reqs_in_sliding_window = self._reqs_in_sliding_window(query_type, current_time,
                                                                          iphone_sliding_window)
                    self._iphone_earliest_next_request_time = min(reqs_in_sliding_window) + iphone_sliding_window + 18
                else:
                    reqs_in_sliding_window = self._reqs_in_sliding_window(query_type, current_time,
                                                                          per_type_sliding_window)
                    self._earliest_next_request_time = min(reqs_in_sliding_window) + per_type_sliding_window + 6
            return max(self._iphone_earliest_next_request_time, self._earliest_next_request_time)

        def iphone_next_request():
            if query_type == "iphone":
                reqs_in_sliding_window = self._reqs_in_sliding_window(query_type, current_time, iphone_sliding_window)
                if len(reqs_in_sliding_window) >= 199:
                    return min(reqs_in_sliding_window) + iphone_sliding_window + 18
            return 0.0

        return max(0.0,
                   max(
                       per_type_next_request_time(),
                       gql_accumulated_next_request_time(),
                       untracked_next_request_time(),
                       iphone_next_request(),
                   ) - current_time)

    def wait_before_query(self, query_type: str) -> None:
        """This method is called before a query to Instagram."""

        waittime = self.query_waittime(query_type, time.monotonic(), False)
        assert waittime >= 0
        if waittime > 15:
            formatted_waittime = ("{} seconds".format(round(waittime)) if waittime <= 666 else
                                  "{} minutes".format(round(waittime / 60)))
            self.logger.info("\nToo many queries in the last time. Need to wait {}, until {:%H:%M}."
                              .format(formatted_waittime, datetime.now() + timedelta(seconds=waittime)))
        if waittime > 0:
            self.sleep(waittime)
        if query_type not in self._query_timestamps:
            self._query_timestamps[query_type] = [time.monotonic()]
        else:
            self._query_timestamps[query_type].append(time.monotonic())

    def handle_429(self, query_type: str) -> None:
        """This method is called to handle a 429 Too Many Requests response."""
        current_time = time.monotonic()
        waittime = self.query_waittime(query_type, current_time, True)
        assert waittime >= 0,"wait time must be greater than or equal to 0"
        self._dump_query_timestamps(current_time, query_type)
        text_for_429 = "Instagram responded with HTTP error 429 - Too Many Requests."
        self.logger.error(text_for_429)

        if waittime > 1.5:
            formatted_waittime = ("{} seconds".format(round(waittime)) if waittime <= 666 else
                                  "{} minutes".format(round(waittime / 60)))
            self.logger.error("The request will be retried in {}, at {:%H:%M}."
                                .format(formatted_waittime, datetime.now() + timedelta(seconds=waittime)))
        if waittime > 0:
            self.sleep(waittime)