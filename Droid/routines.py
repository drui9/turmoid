from Droid import Android
from loguru import logger


# @Android.routine(5)
# def update_contacts():
# 	logger.critical('updating contact list')

# @Android.routine(4)
# def check_sms():
# 	logger.critical('checking sms inbox')

@Android.routine(3)
def check_call_log():
	logger.critical('checking call logs')

@Android.routine(2)
def check_battery():
	logger.critical('checking battery')
