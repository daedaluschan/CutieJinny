import os

log_file_size_lmt = 10485760
log_file_count_lmt = 5


TOKEN = os.environ['CUTE_TOKEN']
file_name = ""
photo_base_dir = ""

LIST_OF_ADMINS = os.environ['ADMIN_LIST']

schedule_time_hh_1 = 10
schedule_time_mm_1 = 00

schedule_time_hh_2 = 15
schedule_time_mm_2 = 15

msg_daily_photo = "今日靚相精選：{}"
