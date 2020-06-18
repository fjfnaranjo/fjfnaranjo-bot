_SECONDS_PER_PORTION = 60 * 5


def aproximate_datetime(datetime):
    date = datetime.date()
    time = datetime.time()
    total_seconds = time.second + (time.minute * 60) + (time.hour * 60 * 60)
    return date, int(total_seconds / _SECONDS_PER_PORTION)


def register_activity(players):
    pass
