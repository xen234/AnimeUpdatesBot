import re

from aiogram import types
from aiogram.utils import executor

from bot_config import dp, database, api
from send_message_function import send_message


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Для просмотра доступных команд отправь /help ")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("В этом боте ты можешь выполнить следующие команды:\n"
                        "/subscribe URL RANGE - оформить подписку на обновления аниме по ссылке\n"
                        "/unsubscribe URL RANGE - оформить подписку на обновления аниме по ссылке\n"
                        "/list - посмотреть список отслеживаемых аниме\n"
                        "/weekly - посмотреть расписание выхода эпизодов отслеживаемых аниме на неделе\n"
                        "В командах subscribe и unsubscribe необходимо передать на вход ссылку "
                        "на интересующее аниме с ресурса MyAnimeList в следующем формате:\n"
                        "https://myanimelist.net/anime/44511/ "
                        "или https://myanimelist.net/anime/44511/Chainsaw_Man")


@dp.message_handler(commands=['list'])
async def process_list_command(message: types.Message):
    anime_list = database.get_tg_subscriptions_by_chat(message.from_user.id)
    await message.reply("Всего отслеживаемых аниме: {}\n".format(len(anime_list)))
    for anime_id in anime_list:
        await send_message(message.from_user.id, api.get_url_by_id(anime_id))


@dp.message_handler(commands=['weekly'])
async def process_weekly_command(message: types.Message):
    anime_list = database.get_tg_subscriptions_by_chat(message.from_user.id)
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        weekday_anime_titles = list()
        anime_on_weekday = api.scheduled_on_week_day(weekday)

        for anime in anime_on_weekday:
            if anime.id in anime_list:
                weekday_anime_titles.append((anime.title, api.get_url_by_id(int(anime.id))))

        if len(weekday_anime_titles):
            await send_message(message.from_user.id, weekday.upper())
            for title, link in weekday_anime_titles:
                await send_message(message.from_user.id, title + '\t' + link)


# ----------------подписка на анимы---------------------------

@dp.message_handler(commands=['subscribe'])
async def process_subscribe_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)

    # try:
    #     input_url = input_url[1]
    #     if 'myanimelist' not in input_url:
    #         raise ValueError
    # except ValueError:
    #     return await message.reply(f"Вы неверно ввели ссылку. Попробуйте еще раз :)")

    # check if suitable
    anime_id = int(api.parse_url(input_url[1])[1])
    database.create_subscription(message.from_user.id, anime_id)
    await message.reply(f"Вы успешно подписались на обновления по следующей ссылке: {input_url[1]}")


@dp.message_handler(commands=['unsubscribe'])
async def process_cancel_subscription_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)
    # try:
    #     input_url = int(input_url[1])
    #     if 'myanimelist' not in input_url:
    #         raise ValueError
    # except ValueError:
    #     return await message.reply(f"Вы неверно ввели ссылку. Попробуйте еще раз :)")

    # check if suitable
    anime_id = int(api.parse_url(input_url[1])[1])
    database.remove_tg_subscription(message.from_user.id, anime_id)
    await message.reply(f"Вы успешно отписались от обновлений по следующей ссылке: {input_url[1]}")


if __name__ == '__main__':
    executor.start_polling(dp)
