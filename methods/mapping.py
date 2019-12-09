# coding=utf-8
import time

from datetime import datetime

from models.history import EVENT_CATEGORY, PERSON_CATEGORY
from models.history import PERIOD_CATEGORY

HTML_STR_DATE_FORMAT = "%Y-%m-%d"
TO_HTML_STR_DATE_FORMAT = "%s-%s-%s"

YOUTUBE_DURATION_FORMAT = "PT%MM%SS"
YOUTUBE_DURATION_SHORT_FORMAT = "PT%MM"
APP_DURATION_WITHOUT_HOURS_FORMAT = "%s:%s"
APP_DURATION_FORMAT = "%s:%s:%s"


def timestamp(datetime_object):
    if datetime_object:
        return int(time.mktime(datetime_object.timetuple()))
    else:
        return 0


def sorted_history_marks(history_marks):
    return sorted(history_marks, key=lambda mark: mark.sort_index)


def get_category(mark_key):
    if mark_key.kind() == 'HistoryPeriod':
        return PERIOD_CATEGORY
    elif mark_key.kind() == 'HistoryEvent':
        return EVENT_CATEGORY
    elif mark_key.kind() == 'HistoryPerson':
        return PERSON_CATEGORY


def mapped_by_group_title(history_marks):
    result = {}
    for mark in history_marks:
        if not result.get(mark.group_title):
            result[mark.group_title] = list()
        result[mark.group_title].append(mark)
    return result


def get_year_title(start, end):
    if start == end:
        return "%s г." % start.year
    else:
        return "%s - %s гг." % (start.year, end.year)


def get_person_year_title(start, end):
    if start == end:
        return "ум. %s г." % start.year
    else:
        return get_year_title(start, end)


def get_date_from_html(date):
    return datetime.strptime(date, HTML_STR_DATE_FORMAT)


def get_html_date_from_str(date):
    year = str(date.year)
    month = str(date.month)
    day = str(date.day)
    if len(year) < 4:
        year = '0' * (4 - len(year)) + year
    if len(month) < 2:
        month = '0' * (2 - len(month)) + month
    if len(day) < 2:
        day = '0' * (2 - len(day)) + day
    return TO_HTML_STR_DATE_FORMAT % (year, month, day)


def get_date_from_youtube(date):
    if 'SS' in date:
        return datetime.strptime(date, YOUTUBE_DURATION_FORMAT)
    else:
        return datetime.strptime(date, YOUTUBE_DURATION_SHORT_FORMAT)


def to_app_duration_format(date):
    def add_zero(time_string):
        if len(time_string) == 1:
            time_string = '0' + time_string
        return time_string

    hours = add_zero(str(date.hour))
    minutes = add_zero(str(date.minute))
    seconds = add_zero(str(date.second))

    if hours == '00':
        return APP_DURATION_WITHOUT_HOURS_FORMAT % (minutes, seconds)
    else:
        return APP_DURATION_FORMAT % (hours, minutes, seconds)


def add_thousands_spaces(date):
    def insert_space(position):
        date_list = list(date)
        date_list.insert(position, ' ')
        return ''.join(date_list)

    if len(date) > 3:
        date = insert_space(len(date) - 3)
    if len(date) > 7:
        date = insert_space(len(date) - 7)

    return date
