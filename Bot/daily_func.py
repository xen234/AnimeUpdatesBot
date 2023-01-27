from datetime import datetime
from send_message_function import send_message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

#should be added to bot_config
scheduler = AsyncIOScheduler()

#should be added to bot.py
@dp.message_handler(commands=['daily'])
async def process_daily_command(message: types.Message):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ok, content = api.scheduled_on_week_day(weekdays[datetime.today().weekday()])
    if not ok:
        await send_message(message.from_user.id, 'Error occurred: ' + content)
        return
    anime_list = content
    for anime in anime_list:
        if not dp.anime_exists(anime.id):
            pass
        users = dp.anime_subscribers(anime.id)
        message = f"New episode of {anime.title} aired! \n" \
                  f"{api.get_url_by_id(anime.id)}"
        for user in users:
            await send_message(user.id, message)

scheduler.add_job(process_daily_command, 'cron', day_of_week='mon-sun',
                  hour=18, minute=30, end_date='2023-05-30')

#should be added in main of bot.py
scheduler.start()
