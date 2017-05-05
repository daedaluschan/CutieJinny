import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
from datetime import date

TOKEN = sys.argv[1]  # get token from command-line

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG,
                    filename="logs/CutieJinny." + str(date.today()) + ".log")

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher


from functools import wraps

LIST_OF_ADMINS = [161517202, 197627552]

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user_id = update.message.from_user.id
        except (NameError, AttributeError):
            try:
                user_id = update.inline_query.from_user.id
            except (NameError, AttributeError):
                try:
                    user_id = update.chosen_inline_result.from_user.id
                except (NameError, AttributeError):
                    try:
                        user_id = update.callback_query.from_user.id
                    except (NameError, AttributeError):
                        print("No user_id available in update.")
                        logging.info("No user_id available in update.")
                        return
        if user_id not in LIST_OF_ADMINS:
            print("唔識你（{}），唔同你講嘢。".format(user_id))
            logging.info("唔識你（{}），唔同你講嘢。".format(user_id))
            bot.sendMessage(chat_id=update.message.chat_id, text="唔識你，唔同你講嘢。")
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="你好，這是可愛小 Jinny Telegram 機械人。")

@restricted
def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="跟人講：" + update.message.text)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
