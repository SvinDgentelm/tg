import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_handler.db_class import Database
from server_api.server_panel import Panel
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


database = Database()

panel = Panel()
panel.test_connect()

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler = AsyncIOScheduler(timezone='Europe/Moscow', jobstores=jobstores)
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())