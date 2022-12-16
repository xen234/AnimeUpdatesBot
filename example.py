import jikan_api
from database import PostgreDB
from models import User, Anime


db = PostgreDB(recreate=False)
api = jikan_api.JikanWrapper()


db.add_user(User(123, "test"))
db.add_user(User(456, "name"))
print(*db.get_users())

ok, anime = api.anime_full(44511)
db.add_anime(anime)
ok, anime = api.anime_full(49918)
db.add_anime(anime)
ok, anime = api.anime_full(21)
db.add_anime(anime)
print(*db.get_all_anime())
print(*db.users_subscriptions(123))
db.add_user(User(123, "test"))
db.subscribe(123, 44511)
db.subscribe(123, 44511)
db.subscribe(456, 44511)
db.subscribe(123, 4)
db.subscribe(123, 67889)
db.subscribe(789, 44511)
print(*db.users_subscriptions(456))
print(*db.anime_subscribers(44511))
db.unsubscribe(123, 44511)
db.close()
