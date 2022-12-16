import requests
import time
import re
from typing import List, Tuple, Union

from models import Anime, AnimeEpisode


class JikanWrapper:
    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4/"
        self.base_anime_url = "https://myanimelist.net/anime/"

    @staticmethod
    def _make_request(url) -> requests.Response:
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(1)
            response = requests.get(url)
        return response

    @staticmethod
    def _make_error_text(status_code) -> str:
        if status_code == 404:
            return "page not found"
        if status_code >= 500:
            return "server error"
        if status_code == 429:
            return "too many requests"
        return "unknown error"

    def get_url_by_id(self, anime_id: int) -> str:
        return self.base_anime_url + str(anime_id) + '/'

    def last_anime_episode(self, anime_id: int) -> Tuple[bool, Union[AnimeEpisode, str]]:
        url = self.base_url + f"anime/{anime_id}/episodes?page=1"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, self._make_error_text(response.status_code)
        data = response.json()
        last_page = data["pagination"]["last_visible_page"]
        if last_page > 1:
            url = self.base_url + f"anime/{anime_id}/episodes?page={last_page}"
            response = JikanWrapper._make_request(url)
            if not response.ok:
                return False, self._make_error_text(response.status_code)
            data = response.json()
        last_episode = data["data"][-1]
        return True, AnimeEpisode(last_episode["url"], last_episode["title"], last_episode["aired"],
                                  last_episode["mal_id"])

    def anime_info(self, anime_id: int) -> Tuple[bool, Union[Anime, str]]:
        url = self.base_url + f"anime/{anime_id}"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, self._make_error_text(response.status_code)
        anime = response.json()
        return True, Anime(anime["mal_id"], anime["url"], anime["title"], anime["broadcast"]["string"])

    def anime_full(self, anime_id: int) -> Tuple[bool, Union[Anime, str]]:
        url = self.base_url + f"anime/{anime_id}"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, self._make_error_text(response.status_code)
        data = response.json()
        anime = data["data"]
        anime_info = Anime(anime["mal_id"], anime["url"], anime["title"], anime["broadcast"]["string"])
        ok, last_ep = self.last_anime_episode(anime_id)
        if ok:
            anime_info.aired_episodes = last_ep.num
        return True, anime_info

    def scheduled_on_week(self) -> Tuple[bool, Union[List[Anime], str]]:
        page = 1
        url = self.base_url + f"schedules?page={page}"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, self._make_error_text(response.status_code)
        data = response.json()
        last_page = data["pagination"]["last_visible_page"]
        anime_list = []
        while page <= last_page:
            url = self.base_url + f"schedules?page={page}"
            response = JikanWrapper._make_request(url)
            if not response.ok:
                return False, self._make_error_text(response.status_code)
            data = response.json()
            for anime in data["data"]:
                anime_list.append(Anime(anime["mal_id"], anime["url"], anime["title"], anime["broadcast"]["string"]))
            page += 1
        return True, anime_list

    def scheduled_on_week_day(self, week_day: str) -> Tuple[bool, Union[List[Anime], str]]:
        page = 1
        url = self.base_url + f"schedules/{week_day}?page={page}"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, self._make_error_text(response.status_code)
        data = response.json()
        last_page = data["pagination"]["last_visible_page"]
        anime_list = []
        while page <= last_page:
            url = self.base_url + f"schedules/{week_day}?page={page}"
            response = JikanWrapper._make_request(url)
            if not response.ok:
                return False, self._make_error_text(response.status_code)
            data = response.json()
            for anime in data["data"]:
                anime_list.append(Anime(anime["mal_id"], anime["url"], anime["title"], anime["broadcast"]["string"]))
            page += 1
        return True, anime_list

    def parse_url(self, url: str) -> Tuple[bool, str]:
        if not url.startswith(self.base_anime_url):
            return False, "wrong prefix"
        response = requests.get(url)
        if response.status_code == 404:
            return False, "invalid url"
        _id = re.findall(r'\d+', url[len(self.base_url):])[0]
        url = self.base_url + f"anime/{_id}"
        response = JikanWrapper._make_request(url)
        if not response.ok:
            return False, "invalid id"
        if response.json()["data"]["type"] != "TV":
            return False, "not a broadcasting anime"
        return True, _id

