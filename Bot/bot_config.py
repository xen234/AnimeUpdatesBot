import logging
from os import environ
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from api import JikanWrapper
from database import PostgreDB


bot = Bot(token=environ['TOKEN'])
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
database = PostgreDB()
api = JikanWrapper()
