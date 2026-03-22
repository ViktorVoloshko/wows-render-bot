import asyncio
import logging

import bot
import config


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    config.init()
    asyncio.run(bot.start())
