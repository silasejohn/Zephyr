import time, datetime

def get_epoch_timestamp(month: int, day: int, year: int) -> int:
    """
    [info] Convert a date (MM, DD, YYYY) to epoch timestamp
    [param] month: Month as integer (1-12)
    [param] day: Day as integer (1-31)
    [param] year: Year as integer (YYYY)
    [return] Epoch timestamp as integer
    """
    return int(time.mktime(datetime.datetime(year, month, day).timetuple()))

def get_current_epoch_timestamp() -> int:
    """
    [info] Get current time as epoch timestamp
    [return] Current epoch timestamp as integer
    """
    return int(time.time())