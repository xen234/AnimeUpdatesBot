import time


class Anime:
    def __init__(self, _id: int, url: str, title: str, broadcast: str, aired_episodes: int = 0, airing: int = 1):
        self.id = _id
        self.url = url
        self.title = title
        self.broadcast = broadcast
        self.aired_episodes = aired_episodes
        self.airing = airing
    
    # for testing
    def __str__(self):
        return f"id = {self.id}, title = {self.title}\nurl = {self.url}\nbroadcast = {self.broadcast} \n" \
            + f"aired = {self.aired_episodes}\n" + f"airing = {self.airing}"


class User:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name

    # for testing
    def __str__(self):
        return f"id = {self.id}, name = {self.name}\n"


class AnimeEpisode:
    def __init__(self, url: str, title: str, aired: str, number: int):
        self.url = url
        self.title = title
        if aired is not None:
            self.aired = time.strptime(aired, "%Y-%m-%dT%H:%M:%S+00:00")
        else:
            self.aired = ""
        self.num = number
