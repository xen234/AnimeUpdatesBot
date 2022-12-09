class Database:
    def __init__(self):
        self.db = {}

    def create_subscription(self, user_id, input_url):
        if user_id not in self.db.keys():
            self.db[user_id] = list()
        self.db[user_id].append(input_url)

    def remove_tg_subscription(self, user_id, input_url):
        if user_id in self.db.keys():
            self.db[user_id].remove(input_url)

    def get_tg_subscriptions_by_chat(self, user_id):
        if user_id in self.db.keys():
            return self.db[user_id]
        else:
            return list()
