from dotenv import load_dotenv
import os

load_dotenv()

telegram_config = {
    'token': os.environ['TELEGRAM_BOT_TOKEN'],
}

discord_config = {
    'token': os.environ['DISCORD_TOKEN'],
}

