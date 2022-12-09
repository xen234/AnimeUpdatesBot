import logging
from os import environ

from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from database import Database, JsonLikeDatabase
from api import JikanWrapper

bot = Bot(token=environ['TOKEN'])
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

database = JsonLikeDatabase()
api = JikanWrapper()
