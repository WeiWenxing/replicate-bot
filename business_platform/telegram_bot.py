import logging
import sys
sys.path.append("..")
from config import telegram_config
from kernel_paint import replicate

from telegram import Message, MessageEntity, Update, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

from kernel_paint.user import User, Database


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
        if user is None:
            await message.reply_text(r'please input your replicate token as /token <apitoken>, you should sign up and get API token: https://replicate.com/account/api-tokens')
        else:
            url = await get_file_url(bot, message)
            success, output = replicate.high_op(url, user.token)
            if success:
                await message.reply_document(output)
            else:
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
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('dress'), self.show_dress))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('bg'), self.show_bg))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('mi'), self.repair_breasts))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('hand'), self.repair_hand))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('lace'), self.lace))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('up'), self.upper))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('lower'), self.lower))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.Caption('ext'), self.ext))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('rep'), self.rep))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('hh'), high))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('clip'), self.clip))
    # application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('all'), self.all))

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

