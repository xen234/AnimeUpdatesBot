import requests
import time
import re
from typing import List, Tuple


class AnimeEpisode:
    def __init__(self, url: str, title: str, aired: str):
        self.url = url
        self.title = title
        self.aired = time.strptime(aired, "%Y-%m-%dT%H:%M:%S+00:00")


class Anime:
    def __init__(self, _id: str, url: str, title: str, broadcast: str):
        self.id = _id
        self.url = url
        self.title = title
        self.broadcast = broadcast


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

    def last_anime_episode(self, anime_id: int) -> AnimeEpisode:
        url = self.base_url + f"anime/{anime_id}/episodes?page=1"
        response = JikanWrapper._make_request(url)
        response.raise_for_status()
        data = response.json()
        last_page = data["pagination"]["last_visible_page"]
        if last_page > 1:
            url = self.base_url + f"anime/{anime_id}/episodes?page={last_page}"
            response = JikanWrapper._make_request(url)
            response.raise_for_status()
            data = response.json()
        last_episode = data["data"][-1]
        return AnimeEpisode(last_episode["url"], last_episode["title"], last_episode["aired"])

    def scheduled_on_week(self) -> List[Anime]:
        page = 1
        url = self.base_url + f"schedules?page={page}"
        response = JikanWrapper._make_request(url)
        response.raise_for_status()
        data = response.json()
        last_page = data["pagination"]["last_visible_page"]
        anime_list = []
        while page <= last_page:
            url = self.base_url + f"schedules?page={page}"
            response = JikanWrapper._make_request(url)
            response.raise_for_status()
            data = response.json()
            for anime in data["data"]:
                anime_list.append(Anime(anime["mal_id"], anime["url"], anime["title"], anime["broadcast"]["string"]))
            page += 1
        return anime_list

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
