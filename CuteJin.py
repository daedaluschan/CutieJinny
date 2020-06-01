import sys, os
from random import  randint
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import replykeyboardmarkup
from telegram import replykeyboardremove
import logging
from logging.handlers import RotatingFileHandler
from datetime import date, time
from re import compile, match

import requests
import json
from random import seed
from urllib import parse
import pathlib
from os.path import basename

from CuteJin_cfg import *

seed()
application = 'FileStation'
login_api = 'auth.cgi?api=SYNO.API.Auth'
logout_api = 'auth.cgi?api=SYNO.API.Auth'

handler =  RotatingFileHandler(filename="logs/CutieJinny.log", maxBytes=log_file_size_lmt, backupCount=log_file_count_lmt)
handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))

logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)


# TOKEN = sys.argv[1]  # get token from command-line
# file_name = sys.argv[2]
# photo_base_dir = sys.argv[3]

def send_photo(bot, recipient):
    with open(file=file_name, mode='r') as f:
        line = f.read()
    f.close()
    photo_path = line.strip()

    logging.info("photo_path : {}".format(photo_path))

    bot.sendPhoto(chat_id=recipient, photo=open(photo_path, 'rb'))



updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

from functools import wraps

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
            print(trc_invalid_id % user_id)
            logging.info(trc_invalid_id % user_id)
            bot.sendMessage(chat_id=update.message.chat_id, text=msg_invalid_id)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

# util for getting immediate sub-directories
def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def get_all_jpg(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.join(a_dir, name).endswith(".JPG")]

markup = replykeyboardmarkup.ReplyKeyboardMarkup(keyboard=kb_start)

@restricted
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, 
                    text=msg_welcome,
                    reply_markup=markup)

def pick_photo_to_send(bot, to_list):

    num_folders = len(photo_base_dir_list)
    picked_base_dir_index = randint(0, num_folders - 1)
    photo_base_dir = photo_base_dir_list[picked_base_dir_index]

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

        for recipient in to_list:
            send_photo(bot=bot, recipient=recipient)
            bot.sendMessage(chat_id=recipient, text=msg_daily_photo.format(photo_desc))

    except(ValueError):
        for recipient in to_list:
            bot.sendMessage(chat_id=recipient, text="Load 唔到相呀。再試過啦。")

def request_data(sid, api_name, api_path, req_param, method=None, response_json=True):  
    # 'post' or 'get' 
    
    # Convert all booleen in string in lowercase because Synology API is waiting for "true" or "false"
    for k,v in req_param.items():
        if isinstance(v, bool):
            req_param[k] = str(v).lower()

    if method is None:
        method = 'get'

    req_param['_sid'] = sid

    if method is 'get':
        url = ('%s%s' % (base_url, api_path)) + '?api=' + api_name
        response = requests.get(url, req_param, verify=False)

        if response_json is True:
            return response.json()
        else:
            return response

    elif method is 'post':
        url = ('%s%s' % (base_url, api_path)) + '?api=' + api_name
        response = requests.post(url, req_param, verify=False)

        if response_json is True:
            return response.json()
        else:
            return response


def sendNasPhoto(bot, to_list):
    
    # Login 

    param = {'version': '2', 
            'method': 'login', 
            'account': usernmae,
            'passwd': pwd, 
            'session': application, 
            'format': 'cookie'}

    session_request = requests.get(base_url + login_api, param, verify=False)
    sid = session_request.json()['data']['sid']

    logging.info('Login compelted')
    logging.info('sid: %s' % sid)
    logging.info(session_request.json())

    # Get full api list

    query_path = 'query.cgi?api=SYNO.API.Info'
    list_query = {'version': '1', 
                'method': 'query', 
                'query': 'all'}
    full_api_list = requests.get(base_url + query_path, list_query, verify=False).json()['data']

    #list folders

    api_name = 'SYNO.FileStation.List'
    info = full_api_list[api_name]
    api_path = info['path']
    req_param = {'version': info['maxVersion'], 
                'method': 'list',
                'folder_path': '%s%s' % (path_prefix, randint(int(start_y), int(end_y))) }

    response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']
    # print(json.dumps(response_file_list, indent=4))
    logging.info('list of folders of length: %s' % len(response_file_list))

    req_param['folder_path'] = response_file_list[randint(0,len(response_file_list)-1)]['path']
    response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']
    # print(json.dumps(response_file_list, indent=4))

    req_param['folder_path'] = response_file_list[randint(0,len(response_file_list)-1)]['path']
    response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']
    # print(json.dumps(response_file_list, indent=4))

    file_download = response_file_list[randint(0,len(response_file_list)-1)]['path']
    print('File to be downloaded : %s' % file_download)


@restricted
def handleMsg(bot, update):
    if(update.message.text == "猩相"):
        send_photo(bot=bot, recipient=update.message.from_user.id)
        # bot.sendPhoto(chat_id=update.message.chat_id, photo=open(photo_path, 'rb'))
        bot.sendMessage(chat_id=update.message.chat_id, text="SENT", reply_markup=markup)
    elif(update.message.text == "換相"):
        pick_photo_to_send(bot=bot, to_list=[update.message.from_user.id])
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="跟人講：" + update.message.text, reply_markup=markup)

def daily_photo(bot, job):
    pick_photo_to_send(bot=bot, to_list=LIST_OF_ADMINS)


jq = updater.job_queue
jq.run_daily(callback=daily_photo, time=time(hour=schedule_time_hh_1, minute=schedule_time_mm_1))
jq.run_daily(callback=daily_photo, time=time(hour=schedule_time_hh_2, minute=schedule_time_mm_2))

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, handleMsg)
dispatcher.add_handler(echo_handler)

updater.start_polling(timeout=30)
