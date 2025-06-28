import asyncio
from create_bot import bot, dp, scheduler
from handlers.start import start_router
from handlers.admin import admin_router

from handlers import scheduler_func

from handlers.users.balance import balance_router
from handlers.users.connect_sub import con_sub_router
from handlers.users.main_menu import main_menu_router
from handlers.users.shop import shop_router
from handlers.users.subscription import sub_router

import uvicorn
from server_api.link_creator import app

async def run_bot():
        
    scheduler.start()
    #dp.include_router(start_router)
    dp.include_router(admin_router)

    dp.include_router(balance_router)
    dp.include_router(con_sub_router)
    dp.include_router(main_menu_router)
    dp.include_router(shop_router)
    dp.include_router(sub_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
