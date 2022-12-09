import time
from jikan_wrapper import JikanWrapper
from database import JsonLikeDatabase


app = JikanWrapper()

print(app.get_title_by_id(44511))


ok, _id = app.parse_url("https://myanimelist.net/anime/44511/Chainsaw_Man")
print(_id)


print(app.get_url_by_id(44511))

# anime_list = [44511, 41467, 49918]
# for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
#     weekday_anime_titles = list()
#     anime_on_weekday = app.scheduled_on_week_day(weekday)
#
#     for anime in anime_on_weekday:
#         print(anime.id)
#         if anime.id in anime_list:
#             weekday_anime_titles.append((anime.title, app.get_url_by_id(int(anime.id))))
#
#     if len(weekday_anime_titles):
#         print(weekday.upper())
#         for title, link in weekday_anime_titles:
#             print(title)
#             print(link)



