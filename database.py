from queries import SqlQueries
import psycopg2
from models import User, Anime
from typing import List


class PostgreDB:
    def __init__(self, recreate=False):
        self.conn = psycopg2.connect(
            database="users", user="postgres", host="localhost", password="password", port=5432)
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
            self.add_anime(Anime(anime_id, "undefined", "undefined", "undefined"))
        if self.check_subscription(user_id, anime_id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.add_reference, str(user_id), str(anime_id)))
            self.conn.commit()

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
            self.add_anime(Anime(anime_id, "undefined", "undefined", "undefined"))
        if not self.check_subscription(user_id, anime_id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.remove_reference, str(user_id), str(anime_id)))
            self.conn.commit()

    def users_subscriptions(self, user_id: int) -> List[Anime]:
        if not self.user_exists(user_id):
            self.add_user(User(user_id, "undefined"))
        res = []
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.subscriptions, str(user_id)))
            for i in range(cur.rowcount):
                res.append(Anime(*cur.fetchone()))
        return res

    def anime_subscribers(self, anime_id: int) -> List[User]:
        if not self.anime_exists(anime_id):
            self.add_anime(Anime(anime_id, "undefined", "undefined", "undefined"))
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

    def update_anime_episodes_info(self, anime_id: int, episodes_num: int):
        if not self.anime_exists(anime_id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.update_anime_episodes, str(episodes_num), str(anime_id)))
            self.conn.commit()

    def update_airing_info(self, anime_id: int, airing: int):
        if not self.anime_exists(anime_id):
            return
        with self.conn.cursor() as cur:
            cur.execute(str.format(*SqlQueries.update_anime_airing_info, str(airing), str(anime_id)))
            self.conn.commit()
    
    def close(self):
        self.conn.close()
