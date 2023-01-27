import json
from typing import List

import psycopg2
import requests
import time

from api import Anime
from database.models import User
from database.queries import SqlQueries


class Database:
    def __init__(self):
        self.db = {}

    def subscribe(self, user_id: str, input_url: str):
        if user_id not in self.db.keys():
            self.db[user_id] = list()
        self.db[user_id].append(input_url)
        return True, None

    def unsubscribe(self, user_id: str, input_url: str):
        if user_id in self.db.keys():
            self.db[user_id].remove(input_url)
        return True, None

    def users_subscriptions(self, user_id: str):
        if user_id in self.db.keys():
            return True, self.db[user_id]
        else:
            return True, list()


class JsonLikeDatabase:
    def __init__(self, path="./", name="base.json"):
        self.base_path = path + name
        with open(self.base_path, "w") as base:
            json.dump({"users": {}}, base)

    def _read_from_db(self):
        with open(self.base_path, "r") as base:
            user_list = json.load(base)
        return user_list

    def _write_to_db(self, data):
        with open(self.base_path, "w") as base:
            json.dump(data, base)

    def add_user(self, user_id: str):
        user_id = str(user_id)
        user_list = self._read_from_db()
        user_subscriptions = []
        user_list["users"][user_id] = user_subscriptions
        self._write_to_db(user_list)

    def subscribe(self, user_id: str, anime_url: str):
        user_id = str(user_id)
        anime_url = str(anime_url)
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
            user_list = self._read_from_db()
        if anime_url in user_list["users"][user_id]:
            return False, "данное аниме уже добавлено"
        user_list["users"][user_id].append(anime_url)
        self._write_to_db(user_list)
        return True, None

    def unsubscribe(self, user_id: str, anime_url: str):
        user_id = str(user_id)
        anime_url = str(anime_url)
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
            user_list = self._read_from_db()
        if anime_url not in user_list["users"][user_id]:
            return False, "такого аниме нет в базе данных"
        user_list["users"][user_id].remove(anime_url)
        self._write_to_db(user_list)
        return True, None

    def users_subscriptions(self, user_id: str):
        user_id = str(user_id)
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
        user_list = self._read_from_db()
        anime_list = user_list["users"][user_id]
        return True, anime_list


class PostgreDB:
    def __init__(self, recreate=False):
        self.conn = psycopg2.connect("host=84.23.53.18 dbname=PostgreSQL-8678 user=sanchmous password=tB71pMP10T8oJ512")
        if recreate:
            with self.conn.cursor() as cur:
                cur.execute(*SqlQueries.create_users_table)
                cur.execute(*SqlQueries.create_anime_table)
                cur.execute(*SqlQueries.create_link_table)
                self.conn.commit()
        else:
            with self.conn.cursor() as cur:
                cur.execute(*SqlQueries.create_users_table_if_not_exists)
                cur.execute(*SqlQueries.create_anime_table_if_not_exists)
                cur.execute(*SqlQueries.create_link_table_if_not_exists)
                self.conn.commit()

    def user_exists(self, _id) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.find_user_by_id, _id))
            return cur.rowcount > 0

    def anime_exists(self, _id) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.find_anime_by_id, _id))
            return cur.rowcount > 0

    def add_user(self, user: User):
        if self.user_exists(user.id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.insert_user, str(user.id), user.name))
            self.conn.commit()

    def add_anime(self, anime: Anime):
        if self.anime_exists(anime.id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.insert_anime,
                                   str(anime.id), anime.url, anime.title, anime.broadcast, anime.aired_episodes))
            self.conn.commit()

    def subscribe(self, user_id: int, anime_id: int):
        if not self.user_exists(user_id):
            self.add_user(User(user_id, "undefined"))
        if not self.anime_exists(anime_id):
            self.add_anime(self.get_anime_info(anime_id))
        if self.check_subscription(user_id, anime_id):
            return False, "вы уже подписаны на это аниме! Не хотите попробовать что-то новое?"
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.add_reference, str(user_id), str(anime_id)))
            self.conn.commit()
        return True, None

    def check_subscription(self, user_id: int, anime_id: int) -> bool:
        if not self.user_exists(user_id):
            return False
        if not self.anime_exists(anime_id):
            return False
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.user_anime_select, str(user_id), str(anime_id)))
            return cur.rowcount > 0

    def unsubscribe(self, user_id: int, anime_id: int):
        if not self.user_exists(user_id):
            self.add_user(User(user_id, "undefined"))
        if not self.anime_exists(anime_id):
            self.add_anime(self.get_anime_info(anime_id))
        if not self.check_subscription(user_id, anime_id):
            return False, "вы не подписаны на это аниме! Выберите аниме, на которое вы подписаны?"
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.remove_reference, str(user_id), str(anime_id)))
            self.conn.commit()
        return True, None

    def users_subscriptions(self, user_id: int) -> (bool, List[Anime]):
        if not self.user_exists(user_id):
            self.add_user(User(user_id, "undefined"))
        res = []
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.subscriptions, str(user_id)))
            for i in range(cur.rowcount):
                res.append(Anime(*cur.fetchone()))
        return True, res

    def anime_subscribers(self, anime_id: int) -> List[User]:
        if not self.anime_exists(anime_id):
            self.add_anime(self.get_anime_info(anime_id))
        res = []
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.subscribers, str(anime_id)))
            for i in range(cur.rowcount):
                res.append(User(*cur.fetchone()))
        return res

    def get_users(self) -> List[User]:
        res = []
        with self.conn.cursor() as cur:
            cur.execute(*SqlQueries.select_all_users)
            for i in range(cur.rowcount):
                res.append(User(*cur.fetchone()))
        return res

    def get_all_anime(self) -> List[Anime]:
        res = []
        with self.conn.cursor() as cur:
            cur.execute(*SqlQueries.select_all_anime)
            for i in range(cur.rowcount):
                res.append(Anime(*cur.fetchone()))
        return res

    def get_anime_by_id(self, anime_id: int) -> Anime:
        res = []
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.find_anime_by_id, str(anime_id)))
            for i in range(cur.rowcount):
                res.append(Anime(*cur.fetchone()))
        return res[0]

    def get_user_by_id(self, user_id: int) -> User:
        res = []
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.find_anime_by_id, str(user_id)))
            for i in range(cur.rowcount):
                res.append(User(*cur.fetchone()))
        return res[0]

    @staticmethod
    def _make_request(url) -> requests.Response:
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(1)
            response = requests.get(url)
        return response

    def get_anime_info(self, anime_id: int) -> Anime:
        url = "https://api.jikan.moe/v4/anime/" + str(anime_id)
        response = self._make_request(url)
        data = response.json()["data"]
        return Anime(data["mal_id"],
                     data["url"],
                     data["title"],
                     data["broadcast"]["string"],
                     0)

    def close(self):
        self.conn.close()
