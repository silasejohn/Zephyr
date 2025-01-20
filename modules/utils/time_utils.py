import time, datetime

# given a MM, DD, YYYY, return the epoch timestamp
def get_epoch_timestamp(month, day, year):
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

# get current time in epoch timestamp
def get_current_epoch_timestamp():
    return int(time.time())