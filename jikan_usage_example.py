import time
from jikan_wrapper import JikanWrapper


app = JikanWrapper()
print(time.strftime('%d/%m/%y %H:%M:%S', app.last_anime_episode(44511).aired))


app.scheduled_on_week_day("Tuesday")
print(len(animes))
for anime in animes:
    print(anime.title)


ok, _id = app.parse_url("https://myanimelist.net/anime/44511/Chainsaw_Man")
