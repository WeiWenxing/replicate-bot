import logging
import os
import asyncio

from business_platform import telegram_bot
from business_platform import discord_bot


def main():

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
        level=logging.INFO
    )

    # Setup and run Discor/Telegram bot

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()

    tasks = [
        discord_bot.start_task(),
        telegram_bot.start_task(),
    ]
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    main()
