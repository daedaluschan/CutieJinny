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

file_name = ""
photo_base_dir = ""

#Timezone are in GMT by default
schedule_time_hh_1 = 23
schedule_time_mm_1 = 00

schedule_time_hh_2 = 11
schedule_time_mm_2 = 15

msg_daily_photo = "今日靚相精選：%s"
msg_same_day_before = "當年今日：%s"

btn_send_photo = 'Send 相'
btn_same_day_before = '當年今日'
kb_start = [[btn_send_photo], [btn_same_day_before]]

trc_invalid_id = 'Invalid user id : %s'
msg_invalid_id = '唔識你，唔同你講嘢。'
msg_welcome = '你好，這是可愛小 Jinny Telegram 機械人。'
msg_no_photo = 'Load 唔到相呀。再試過啦。'

btn_more_that_day = '更多同日相片'

msg_date_no_photo = '呢一日冇相喎：%s'
file_size_limit = 2097152
target_pixel_L = 2016