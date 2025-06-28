# main.py

import asyncio
import uvicorn
from aiogram_run import run_bot
from server_api.link_creator import app


async def start_api():
    config = uvicorn.Config(app, host="217.60.39.40", port=8000, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        start_api(),
        run_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())