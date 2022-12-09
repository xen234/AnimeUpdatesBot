from send_message_function import send_message
import re
from bot_config import dp
from aiogram import types
from aiogram.utils import executor


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Для просмотра доступных команд отправь /help ")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("В этом боте ты можешь выполнить следующие команды:\n"
                        "/list - посмотреть список отслеживаемых аниме\n"
                        "/subscribe URL RANGE - оформить подписку на обновления аниме по ссылке\n"
                        "/unsubscribe URL RANGE - оформить подписку на обновления аниме по ссылке\n"
                        "/weekly - посмотреть расписание выхода эпизодов отслеживаемых аниме на неделе\n"
                        "В командах subscribe и unsubscribe необходимо передать на вход ссылку "
                        "на интересующее аниме с ресурса MyAnimeList в следующем формате:\n"
                        "https://myanimelist.net/anime/44511/ "
                        "или https://myanimelist.net/anime/44511/Chainsaw_Man")


@dp.message_handler(commands=['list'])
async def process_info_command(message: types.Message):
    await message.reply(f"Всего отслеживаемых аниме: "
                        f"\n")


# ----------------подписка на анимы---------------------------

@dp.message_handler(commands=['subscribe'])
async def process_subscribe_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)

    try:
        input_url = int(input_url[1])
        if 'myanimelist' not in input_url:
            raise ValueError
    except ValueError:
        return await message.reply(f"Вы неверно ввели ссылку. Попробуйте еще раз :)")

    # check if suitable
    database.create_subscription(message.from_user.id, input_url)
    await message.reply(f"Вы успешно подписались на обновления по следующей ссылке: {input_url}")


@dp.message_handler(commands=['unsubscribe'])
async def process_cancel_subscription_command(message: types.Message):
    await message.reply(f"На вход необходимо подать ссылку. Подробности можно узнать,"
                        f" воспользовавшись командой /help")
    input_url = re.split(' ', message.text, maxsplit=3)
    try:
        input_url = int(input_url[1])
        if 'myanimelist' not in input_url:
            raise ValueError
    except ValueError:
        return await message.reply(f"Вы неверно ввели ссылку. Попробуйте еще раз :)")

    # check if suitable
    database.remove_tg_subscription(message.from_user.id, input_url)
    await message.reply(f"Вы успешно отписались от обновлений по следующей ссылке: {input_url}")


@dp.message_handler(lambda message: len(database.get_tg_subscriptions_by_chat(message.chat.id)))
async def process_forward_command(message: types.Message):
    subscriptions = database.get_tg_subscriptions_by_chat(message.chat.id)
    print(subscriptions)
    if message_classifier.is_important(message.text):
        for user in subscriptions:
            await send_message(user.user_id, message.text)


if __name__ == '__main__':
    executor.start_polling(dp)

    
