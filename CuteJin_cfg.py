import os

log_file_size_lmt = 10485760
log_file_count_lmt = 5

# Specific folder structure of how my own NAS is storing the photos
start_y = os.environ['JIN_FROM_YYYY']
end_y = os.environ['JIN_TO_YYYY']

path_prefix = os.environ['NAS_PHOTO_PREFIX']
ip = os.environ['NAS_IP']
port = os.environ['NAS_PORT']
usernmae = os.environ['NAS_USR']
pwd = os.environ['NAS_PWD']

base_url = 'https://%s:%s/webapi/' % (ip, port)

TOKEN = os.environ['CUTE_TOKEN']
LIST_OF_ADMINS = os.environ['ADMIN_LIST'].split(',')
#LIST_OF_ADMINS = os.environ['SUPER_ADMIN']


file_name = ""
photo_base_dir = ""

#Timezone are in GMT by default
schedule_time_hh_1 = 23
schedule_time_mm_1 = 00

schedule_time_hh_2 = 11
schedule_time_mm_2 = 15

msg_daily_photo = "今日靚相精選：%s"

btn_send_photo = 'Send 相'
kb_start = [[btn_send_photo]]

trc_invalid_id = 'Invalid user id : %s'
msg_invalid_id = '唔識你，唔同你講嘢。'
msg_welcome = '你好，這是可愛小 Jinny Telegram 機械人。'
msg_no_photo = 'Load 唔到相呀。再試過啦。'