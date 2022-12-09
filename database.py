import json


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
        user_list = self._read_from_db()
        user_subscriptions = []
        user_list["users"][user_id] = user_subscriptions
        self._write_to_db(user_list)

    def subscribe(self, user_id: str, anime_url: str):
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
        user_list["users"][user_id].append(anime_url)
        self._write_to_db(user_list)
        return True, None

    def users_subscriptions(self, user_id: str):
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
        anime_list = user_list["users"][user_id]
        return True, anime_list

    def unsubscribe(self, user_id: str, anime_url: str):
        user_list = self._read_from_db()
        if user_id not in user_list["users"]:
            self.add_user(user_id)
        if anime_url not in user_list["users"][user_id]:
            return False, "anime not found"
        user_list["users"][user_id].remove(anime_url)
        self._write_to_db(user_list)
        return True, None
