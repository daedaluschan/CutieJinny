import sys, os
from telegram.ext import Updater
from datetime import date
import logging
from random import randint
from re import compile, match

TOKEN = sys.argv[1]  # get token from command-line
file_name = sys.argv[2]
photo_base_dir = sys.argv[3]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG,
                    filename="logs/MorningJinny." + str(date.today()) + ".log")

LIST_OF_ADMINS = [161517202, 197627552]

updater = Updater(token=TOKEN)

# util for getting immediate sub-directories from a directory (a_dir)
def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

# util for getting immediate JPGs from a directory (a_dir)
def get_all_jpg(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.join(a_dir, name).endswith(".JPG")]


def send_photo(bot, chat_id):
    with open(file=file_name, mode='r') as f:
        line = f.read()
    f.close()
    photo_path = line.strip()

    logging.info("photo_path : {}".format(photo_path))

    bot.sendPhoto(chat_id=chat_id, photo=open(photo_path, 'rb'))


try:
    dir_list = get_immediate_subdirectories(photo_base_dir)
    size = len(dir_list)
    picked_index = randint(0, size - 1)
    picked_dir = photo_base_dir + "/" + dir_list[picked_index]
    logging.info("Picked Dir : {}".format(picked_dir))

    sub_dir_list = get_immediate_subdirectories(picked_dir)
    sub_dir_size = len(sub_dir_list)
    picked_sub_index = randint(0, sub_dir_size - 1)
    picked_sub_dir = picked_dir + "/" + sub_dir_list[picked_sub_index]
    logging.info("Picked Sub Dir : {}".format(picked_sub_dir))

    photo_list = get_all_jpg(picked_sub_dir)
    num_of_photo = len(photo_list)
    picked_photo_index = randint(0, num_of_photo - 1)
    picked_photo = picked_sub_dir + "/" + photo_list[picked_photo_index]
    logging.info("Picked PHOTO : {}".format(picked_photo))

    with open(file_name, mode='w') as f:
        f.write(picked_photo)

    photo_desc = compile('.*\/(\d\d\d\d_\d\d_\d\d\@Day[^/]+)\/.*').match(picked_photo).group(1)
    logging.info("Photo_info: {}".format(photo_desc))

    for admin_id in LIST_OF_ADMINS:
        send_photo(updater.bot, admin_id)
        updater.bot.send_message(chat_id=admin_id, text="今日靚相精選：{}".format(photo_desc))

except(ValueError):
    for admin_id in LIST_OF_ADMINS:
        updater.bot.send_message(chat_id=admin_id, text="今日 rand 唔到新相。")

updater.stop()
