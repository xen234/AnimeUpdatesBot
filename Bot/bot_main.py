import re
from aiogram import types
from aiogram.utils import executor

from bot_config import dp, database
from bot_config import api, scheduler
from utils import send_message
from datetime import datetime


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Для просмотра доступных команд набери /help ")


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
    ok, content = database.users_subscriptions(str(message.from_user.id))
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
    anime_list = content
    await message.reply("Всего отслеживаемых аниме: {}\n".format(len(anime_list)))
    for anime in anime_list:
        response = "Название: " + anime.title + "\n" + "Расписание выхода серий (по японскому времени): " + anime.broadcast + \
                   "\n" + "Вышло эпизодов: " + str(anime.aired_episodes) + "\n" + "Ссылка: " + anime.url
        await send_message(message.from_user.id, response)


@dp.message_handler(commands=['weekly'])
async def process_weekly_command(message: types.Message):
    ok, content = database.users_subscriptions(str(message.from_user.id))
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
    anime_list = content
    await message.reply("Всего отслеживаемых аниме: {}\n".format(len(anime_list)))
    message_from_bot = ''
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        ok, content = api.scheduled_on_week_day(weekday)
        if not ok:
            await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
            return

        message_weekday = ''
        for anime in content:
            if anime.id in list(map(lambda a: a.id, anime_list)):
                message_weekday += anime.title + '\t' + api.get_url_by_id(anime.id) + '\n'

        if len(message_weekday):
            message_from_bot += weekday.upper() + ':\n' + message_weekday

    if not len(message_from_bot):
        await send_message(message.from_user.id, 'Календарь этой недели пуст - нет отслеживаемых аниме')
        return
    await send_message(message.from_user.id, message_from_bot)


# ----------------подписка на анимы---------------------------

@dp.message_handler(commands=['subscribe'])
async def process_subscribe_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)

    ok, content = api.parse_url(input_url[1])
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
        return
    anime_id = content
    ok, content = database.subscribe(str(message.from_user.id), anime_id)
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
    await message.reply(f"Вы успешно подписались на обновления по следующей ссылке: {input_url[1]}")


@dp.message_handler(commands=['unsubscribe'])
async def process_cancel_subscription_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)

    ok, content = api.parse_url(input_url[1])
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
        return
    anime_id = content
    ok, content = database.unsubscribe(str(message.from_user.id), anime_id)
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
    await message.reply(f"Вы успешно отписались от обновлений по следующей ссылке: {input_url[1]}")


@dp.message_handler(commands=['daily'])
async def process_daily_command(message: types.Message):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ok, content = api.scheduled_on_week_day(weekdays[datetime.today().weekday()])
    if not ok:
        await send_message(message.from_user.id, 'Возникла ошибка: ' + content)
        return
    anime_list = content
    for anime in anime_list:
        if not database.anime_exists(anime.id):
            pass
        users = database.anime_subscribers(anime.id)
        response = f"Вышел новый эпизод аниме {anime.title}! \n" \
                   f"{api.get_url_by_id(anime.id)}"
        for user in users:
            await send_message(user.id, response)


if __name__ == '__main__':
    scheduler.add_job(process_daily_command, 'cron', day_of_week='mon-sun',
                      hour=16, minute=13, end_date='2023-05-30', args=(dp,))
    scheduler.start()
    executor.start_polling(dp)
