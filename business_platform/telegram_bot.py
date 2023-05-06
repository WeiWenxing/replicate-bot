import logging
import sys
sys.path.append("..")

import datetime
from PIL import Image, PngImagePlugin, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO

from telegram import Message, MessageEntity, Update, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

from config import telegram_config
from kernel_paint import replicate
from kernel_paint.user import User, Database
from kernel_paint import mask_clipseg

db = Database('tel.db')


def message_text(message: Message) -> str:
    """
    Returns the text of a message, excluding any bot commands.
    """
    message_text = message.text
    if message_text is None:
        return ''

    for _, text in sorted(message.parse_entities([MessageEntity.BOT_COMMAND]).items(), key=(lambda item: item[0].offset)):
        message_text = message_text.replace(text, '').strip()

    return message_text if len(message_text) > 0 else ''


commands = [
    BotCommand(command='help', description='Show help message'),
    BotCommand(command='draw', description='draw a picture'),
    BotCommand(command='token', description='please input your replicate token, you should sign up and get your API token: https://replicate.com/account/api-tokens'),
]


async def get_file_url(bot, message):
    logging.info("Message contains one photo.")
    file = await bot.getFile(message.photo[-1].file_id)
    logging.info(file)
    file_url = file.file_path
    logging.info(file_url)
    return file_url


async def down_image_to_path(bot, message):
    logging.info("Message contains one photo.")
    date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    path = f'download/photo_{date}.jpg'
    logging.info(f"{path}")
    file = await bot.getFile(message.photo[-1].file_id)
    logging.info(file)
    photo_path = await file.download_to_drive(custom_path=path)
    logging.info(photo_path)
    return str(photo_path)


def open_image_from_path(photo_path):
    logging.info(photo_path)
    with open(photo_path, "rb") as f:
        file_bytes = f.read()
    image = Image.open(BytesIO(file_bytes))
    return image


def save_image(image: Image, fileName, quality=100, mode='JPEG'):
    ext = 'png' if mode == 'PNG' else 'jpg'
    image.save(f'{fileName}.{ext}', mode, quality=quality)
    return f'{fileName}.{ext}'


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows the help menu.
    """
    commands_description = [f'/{command.command} - {command.description}' for command in commands]
    help_text = 'I\'m a SD bot, talk to me!' + \
                '\n\n' + \
                '\n'.join(commands_description) + \
                '\n\n' + \
                'Send me a image and I\'ll transcribe it for you!'
    await update.message.reply_text(help_text, disable_web_page_preview=True)


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    logging.info(message.text)
    strs = message.text.split()
    logging.info(strs)
    if len(strs) < 2:
        await message.reply_text(r'please input your replicate token as /token <apitoken>, you should sign up and get API token: https://replicate.com/account/api-tokens')
        return

    rep_token = strs[1]
    id = str(message.from_user.id)
    logging.info(id)
    user = db.get_user(id)
    logging.info(user)
    if user is None:
        user = User(id=id, token=rep_token, points=0, cash=0)
        db.add_user(user)
    else:
        user.token = rep_token
        db.update_user(user)
    new_user = db.get_user(id)
    logging.info(new_user)
    await message.reply_text(f'{new_user}')


async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    logging.info(message.text)
    strs = message.text.split()
    logging.info(strs)
    if len(strs) < 2:
        await message.reply_text(r'please input points as /points <points>')
        return

    points = int(strs[1])
    id = str(message.from_user.id)
    logging.info(id)
    user = db.get_user(id)
    logging.info(user)
    if user is not None:
        user.points += points
        db.update_user(user)
        new_user = db.get_user(id)
        logging.info(new_user)
        await message.reply_text(f'{new_user}')


async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    await message.reply_text("draw")


async def high(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot = context.bot
    if message.photo:
        id = str(message.from_user.id)
        logging.info(id)
        user = db.get_user(id)
        logging.info(user)
        if not user or not user.token:
            await message.reply_text(f'please input your replicate token as: /token <apitoken>。\n  You should sign in and get API token: https://replicate.com/account/api-tokens')
        else:
            url = await get_file_url(bot, message)
            success, output = replicate.high_op(url, user.token)
            if success:
                await message.reply_document(output)
            else:
                user.token = ''
                db.update_user(user)
                await message.reply_text(output)


async def trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot = context.bot
    if message.photo:
        id = str(message.from_user.id)
        user = db.get_user(id)
        if not user or not user.token:
            await message.reply_text(f'please input your replicate token as: /token <apitoken>。\n  You should sign in and get API token: https://replicate.com/account/api-tokens')
        else:
            url = await get_file_url(bot, message)
            image_path = await down_image_to_path(bot, message)
            image = open_image_from_path(image_path)
            mask = mask_clipseg.run(image, "dress|clothes|bra|underwear|pants", "face|mask", mask_precision=100, mask_padding=4)

            date = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
            mask_name = f'download/mask_{date}'
            mask_path = save_image(mask, mask_name, mode='PNG')
            logging.info(mask_path)

            await message.reply_photo(mask_path)
            import numpy as np

            mask_l = mask.convert("L")
            mask_array = np.array(mask_l)
            mask_array = np.invert(mask_array)#np.logical_not(mask).astype(np.uint8)
            mask_invert = Image.fromarray(mask_array)
            merge = Image.composite(image, Image.new("RGB", image.size, "black"), mask_invert)
            merge_name = f'download/merge_{date}'
            merge_path = save_image(merge, merge_name, quality=90, mode='JPEG')
            await message.reply_photo(merge_path)
            return

            prompt = r'(8k, RAW photo, best quality, masterpiece:1.2), 3d, (realistic, photo-realistic:1.37), fmasterpiecel, 1girl, extremely delicate facial, perfect female figure, (absolutely nude:1.6), smooth fair skin, procelain skin, lustrous skin, clavicle, cleavage, slim waist, very short hair, arms in back, an extremely delicate and beautiful, extremely detailed,intricate,'
            prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), easynegative, badhandsv5, skin spots, acnes, skin blemishes, tattoo, body painting, age spot, (ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3), (saggy breasts:1.3)'

            success, output = replicate.nude_op(token=user.token, image=url, mask=mask_path, prompt=prompt, negative_prompt=prompt_negative)
            if success:
                for img in output:
                    await message.reply_document(img)
                # await message.reply_text(output)
            else:
                user.token = ''
                db.update_user(user)
                await message.reply_text(output)


async def run():
    """
    Runs the bot indefinitely until the user presses Ctrl+C
    """
    application = ApplicationBuilder() \
        .token(telegram_config['token']) \
        .concurrent_updates(True) \
        .build()

    application.add_handler(CommandHandler('draw', draw))
    application.add_handler(CommandHandler('start', help))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('token', token))
    application.add_handler(CommandHandler('points', points))

    # application.add_handler(CallbackQueryHandler(callback=self.set_model, pattern='GuoFeng|chill|uber|majic'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_dress, pattern='.*dress|.*suit|.*wear|.*uniform|armor|hot|bikini|see|.*hanfu'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_bg, pattern='.*beach|grass|space|street|mountain'))

    # application.add_handler(MessageHandler(filters.PHOTO & ~filters.CaptionRegex('dress|bg|mi|hand|lace|up|lower|ext|rep|high|clip|all'), self.trip))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('hh'), high))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('tt'), trip))

    #application.add_error_handler(self.error_handler)

    # application.run_polling()
    await application.initialize()
    await application.start()
    logging.info("start up successful ……")
    await application.updater.start_polling(drop_pending_updates=True)


async def start_task():
    """|coro|
    以异步方式启动
    """
    return await run()

