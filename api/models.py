import time


class AnimeEpisode:
    def __init__(self, url: str, title: str, aired: str, number: int):
        self.url = url
        self.title = title
        if aired is not None:
            self.aired = time.strptime(aired, "%Y-%m-%dT%H:%M:%S+00:00")
        else:
            self.aired = ""
        self.num = number


class Anime:
    def __init__(self, _id: int, url: str, title: str, broadcast: str, aired_episodes: int = 0):
        self.id = _id
        self.url = url
        self.title = title
        self.broadcast = broadcast
        self.aired_episodes = aired_episodes

    # for testing
    def __str__(self):
        return f"id = {self.id}, title = {self.title}\nurl = {self.url}\nbroadcast = {self.broadcast} \n" \
            + f"aired = {self.aired_episodes}\n"
