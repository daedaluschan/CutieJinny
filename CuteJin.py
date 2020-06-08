import sys, os, shutil
from random import  randint
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import replykeyboardmarkup
from telegram import replykeyboardremove
from telegram.inline import inlinekeyboardbutton, inlinekeyboardmarkup
import logging
from logging.handlers import RotatingFileHandler
from datetime import date, time

import requests
import json
from random import seed
from urllib import parse
import pathlib
from os.path import basename
from re import match, compile
from PIL import Image, ExifTags
from resizeimage import resizeimage

from CuteJin_cfg import *

seed()
application = 'FileStation'
login_api = 'auth.cgi?api=SYNO.API.Auth'
logout_api = 'auth.cgi?api=SYNO.API.Auth'

logs_folder = pathlib.Path(__file__).parent.absolute().__str__() + '/logs/'
pathlib.Path(logs_folder).mkdir(parents=True, exist_ok=True)
this_file=__file__

handler =  RotatingFileHandler(filename="logs/CutieJinny.log", maxBytes=log_file_size_lmt, backupCount=log_file_count_lmt)
handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s'))

logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)

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
        if user_id.__str__() not in LIST_OF_ADMINS:
            print(trc_invalid_id % user_id)
            logging.info(trc_invalid_id % user_id)
            bot.sendMessage(chat_id=update.message.chat_id, text=msg_invalid_id)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped



markup = replykeyboardmarkup.ReplyKeyboardMarkup(keyboard=kb_start)

@restricted
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, 
                    text=msg_welcome,
                    reply_markup=markup)

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


def sendNasPhoto(bot, to_list, given_folder=None, given_date=None):
    
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

    year_to_pick = None
    if given_date is None:
        year_to_pick = randint(int(start_y), int(end_y))
    else:
        year_to_pick = given_date.year

    
    #list folders
    api_name = 'SYNO.FileStation.List'
    info = full_api_list[api_name]
    api_path = info['path']
    req_param = {'version': info['maxVersion'], 
                'method': 'list',
                'folder_path': '%s%s' % (path_prefix, year_to_pick) }

    if given_folder == None:
        response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']
        logging.info('list of folders of length: %s' % len(response_file_list))

        if given_date is None:
            req_param['folder_path'] = response_file_list[randint(0,len(response_file_list)-1)]['path']
        else:
            folder_prefix = str(given_date.year) \
                            + '_' + str(given_date.month).zfill(2) \
                            + '_' + str(given_date.day).zfill(2)
            for index, folder in enumerate(response_file_list):
                if folder_prefix in folder['path']:
                    req_param['folder_path'] = folder['path']
                    break
                elif index == len(response_file_list)-1:
                    for recipient in to_list:
                        bot.sendMessage(chat_id=recipient, text=msg_date_no_photo % folder_prefix)
                    return

    else:
        req_param['folder_path'] = given_folder
    
    response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']

    req_param['folder_path'] = response_file_list[randint(0,len(response_file_list)-1)]['path']
    response_file_list = request_data(sid, api_name, api_path, req_param)['data']['files']

    file_download=''
    file_name=''

    for i in range(1,3):
        file_download = response_file_list[randint(0,len(response_file_list)-1)]['path']

        if file_download.upper().endswith('.JPG') or file_download.upper().endswith('.JPEG'):
            logging.info('File to be downloaded : %s' % file_download)
            file_name = basename(file_download)
            break

    if file_name == '':
        for recipient in to_list:
            bot.sendMessage(chat_id=recipient, text=msg_no_photo)
    else:
        api_name = 'SYNO.FileStation.Download'
        info = full_api_list[api_name]
        api_path = info['path']
        
        save_folder = pathlib.Path(this_file).parent.absolute().__str__() + '/photo/'
        pathlib.Path(save_folder).mkdir(parents=True, exist_ok=True)
        save_path = save_folder + file_name

        session = requests.session()
        url = ('%s%s' % (base_url, api_path)) \
            + '?api=%s&version=%s&method=download&path=%s&mode=download&_sid=%s' \
            % (api_name, info['maxVersion'], parse.quote_plus(file_download), sid)

        logging.info('url : %s' % url)
        
        with session.get(url, stream=True, verify=False) as r:
            r.raise_for_status()
            logging.info('save_path: %s' % basename(save_path))
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

        photo_desc = file_download.split('/')[-3]
        file_size = os.path.getsize(save_path)
        logging.info('file size: %s' % file_size)

        if file_size > file_size_limit:
            logging.info('Resizing...')
            with open(save_path, 'r+b') as f:
                with Image.open(f) as image:
                    if hasattr(image, '_getexif'):
                        exif = image._getexif()
                        if exif:
                            for tag, label in ExifTags.TAGS.items():
                                if label == 'Orientation':
                                    orientation = tag
                                    break
                            
                            if orientation in exif:
                                if exif[orientation] == 3:
                                    image = image.rotate(180, expand=True)
                                elif exif[orientation] == 6:
                                    image = image.rotate(270, expand=True)
                                elif exif[orientation] == 8:
                                    image = image.rotate(90, expand=True)
                    
                    if image.size[0] > image.size[1]:
                        new_H = target_pixel_L
                        new_W = int((target_pixel_L / image.size[0]) * image.size[1])
                    else:
                        new_W = target_pixel_L
                        new_H = int((target_pixel_L / image.size[1]) * image.size[0])
                    
                    image = resizeimage.resize_thumbnail(image, [new_H, new_W])
                    image.save(save_path)
        
        
        for recipient in to_list:
            download_folder = parse.quote_plus(str(pathlib.Path(file_download).parent.parent.absolute()))
            logging.info('download_folder: %s' % download_folder)
            inline_button = inlinekeyboardbutton.InlineKeyboardButton(btn_more_that_day, 
                                                                    callback_data=download_folder)
            reply_markup=inlinekeyboardmarkup.InlineKeyboardMarkup([[inline_button]])
            
            logging.info('chat id: %s' % recipient)
            bot.sendPhoto(chat_id=recipient, photo=open(save_path, 'rb'))
            bot.sendMessage(chat_id=recipient, 
                            text=msg_daily_photo % str(photo_desc), 
                            reply_markup=reply_markup)
        
        cleanup(save_folder)

def cleanup(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.info('Failed to delete %s. Reason: %s' % (file_path, e))

@restricted 
def handle_cb(bot, update):

    logging.info("Entering handle_cb()")

    given_folder = parse.unquote_plus(str(update.callback_query["data"]))
    logging.info('given_folder: %s' % given_folder)

    sendNasPhoto(bot, to_list=LIST_OF_ADMINS, given_folder=given_folder)

@restricted
def handleMsg(bot, update):
    if(update.message.text == btn_send_photo):
        sendNasPhoto(bot=bot, to_list=LIST_OF_ADMINS)
    elif compile('(\d{8})').match(update.message.text) is not None:
        match_obj = compile('(\d{8})').match(update.message.text)
        in_str = match_obj.group(1)
        logging.info('in_str: %s' % in_str)
        date_str = ''
        
        for charact in in_str:
            if charact.isdigit():
                date_str = date_str + charact
        
        logging.info('date_str: %s' % date_str)
        theDate = date(int(date_str[0:4]),int(date_str[4:6]),int(date_str[6:8]))

        sendNasPhoto(bot, LIST_OF_ADMINS, given_date=theDate)
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="跟人講：" + update.message.text, reply_markup=markup)

def daily_photo(bot, job):
    sendNasPhoto(bot=bot, to_list=LIST_OF_ADMINS)


jq = updater.job_queue
jq.run_daily(callback=daily_photo, time=time(hour=schedule_time_hh_1, minute=schedule_time_mm_1))
jq.run_daily(callback=daily_photo, time=time(hour=schedule_time_hh_2, minute=schedule_time_mm_2))

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, handleMsg)
dispatcher.add_handler(echo_handler)

cb_handler = CallbackQueryHandler(handle_cb)
dispatcher.add_handler(cb_handler)

updater.start_polling(timeout=30)
