import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import replykeyboardmarkup
from telegram import replykeyboardremove
import logging
from datetime import date

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG,
                    filename="logs/CutieJinny." + str(date.today()) + ".log")

TOKEN = sys.argv[1]  # get token from command-line
file_name = sys.argv[2]
# photo_path = ""

def send_photo(bot, update):
    with open(file=file_name, mode='r') as f:
        line = f.read()
    f.close()
    photo_path = line.strip()

    logging.info("photo_path : {}".format(photo_path))

    bot.sendPhoto(chat_id=update.message.chat_id, photo=open(photo_path, 'rb'))



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

markup = replykeyboardmarkup.ReplyKeyboardMarkup(keyboard=[["猩相"],["換相"]])

@restricted
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="你好，這是可愛小 Jinny Telegram 機械人。",
                    reply_markup=markup)

@restricted
def handleMsg(bot, update):
    if(update.message.text == "猩相"):
        send_photo(bot=bot, update=update)
        # bot.sendPhoto(chat_id=update.message.chat_id, photo=open(photo_path, 'rb'))
        bot.sendMessage(chat_id=update.message.chat_id, text="SENT", reply_markup=markup)
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="跟人講：" + update.message.text, reply_markup=markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, handleMsg)
dispatcher.add_handler(echo_handler)

updater.start_polling()
