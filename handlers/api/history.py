# coding=utf-8
from datetime import datetime, timedelta
from functools import partial
from operator import is_not

from google.appengine.api import memcache

from handlers.api.base import ApiHandler
from methods import mapping
from methods.mapping import sorted_history_marks, get_category, timestamp
from methods.strings import MEM_CACHE_MARK_INFO_KEY_MASK, MEM_CACHE_PERIODS_KEY_MASK, MEM_CACHE_TIME, \
    MEM_CACHE_NEW_MARKS_KEY_MASK
from models.book import Book
from models.history import HistoryCountry, HistoryPeriod, HistoryPerson, MARK_CATEGORIES, PERIOD_CATEGORY, HistoryEvent, \
    EVENT_CATEGORY, PERSON_CATEGORY, VIDEO_CATEGORY
from models.video import YoutubeVideo, YoutubeChannel


class TimestampHistoryPeriodsHandler(ApiHandler):
    def get(self):
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        self.render_json({
            'timestamp': str(timestamp(country.updated))
        })


class HistoryPeriodsHandler(ApiHandler):
    def get(self):
        def get_periods():
            periods = memcache.get(key=MEM_CACHE_PERIODS_KEY_MASK % country.key.id())
            if not periods:
                periods = HistoryPeriod.query(HistoryPeriod.country == country.key).fetch()
                memcache.add(key=MEM_CACHE_PERIODS_KEY_MASK % country.key.id(), value=periods, time=MEM_CACHE_TIME)
            return periods

        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        self.render_json({
            'periods': [period.dict() for period in sorted_history_marks(get_periods())],
            'timestamp': str(timestamp(country.updated))
        })


class HistoryMarkInfoHandler(ApiHandler):
    @staticmethod
    def get_mark_dict(mark):
        result = memcache.get(key=MEM_CACHE_MARK_INFO_KEY_MASK % (mark.category, mark.key.id()))
        if result is not None:
            return result

        events = sorted_history_marks(HistoryEvent.get_by_mark(mark))
        persons = sorted_history_marks(HistoryPerson.get_by_mark(mark))
        videos = sorted_history_marks(YoutubeVideo.get_by_mark(mark))
        channels = filter(partial(is_not, None), (YoutubeChannel.get_by_channel_id(channel_id=channel_id)
                                                  for channel_id in set([video.channel_id for video in videos])))
        books = sorted_history_marks(Book.get_by_mark(mark))

        result = {
            'text': mark.text.get().dict(),
            'events': [event.dict() for event in events],
            'persons': [person.dict() for person in persons],
            'videos': [video.dict() for video in videos],
            'channels': [channel.dict() for channel in channels],
            'books': [book.dict() for book in books],
            'test': mark.test.get().dict(),
            'dependencies': [{
                'id': str(dependency.id()),
                'category': str(get_category(dependency)),
            } for dependency in mark.dependencies],
        }
        memcache.add(key=MEM_CACHE_MARK_INFO_KEY_MASK % (mark.category, mark.key.id()), value=result, time=MEM_CACHE_TIME)

        return result

    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category not in MARK_CATEGORIES:
            self.abort(400)
        if category == PERIOD_CATEGORY:
            period = HistoryPeriod.get_by_id(mark_id)
            if not period:
                self.abort(400)
            self.render_json(self.get_mark_dict(period))
        elif category == EVENT_CATEGORY:
            event = HistoryEvent.get_by_id(mark_id)
            if not event:
                self.abort(400)
            self.render_json(self.get_mark_dict(event))
        elif category == PERSON_CATEGORY:
            person = HistoryPerson.get_by_id(mark_id)
            if not person:
                self.abort(400)
            self.render_json(self.get_mark_dict(person))


class ShortHistoryMarkInfoHandler(ApiHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category not in [EVENT_CATEGORY, PERSON_CATEGORY]:
            self.abort(400)
        elif category == EVENT_CATEGORY:
            event = HistoryEvent.get_by_id(mark_id)
            if not event:
                self.abort(400)
            self.render_json(event.dict())
        elif category == PERSON_CATEGORY:
            person = HistoryPerson.get_by_id(mark_id)
            if not person:
                self.abort(400)
            self.render_json(person.dict())


class PeriodOfMarkInfoHandler(ApiHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        period = None
        if category == PERIOD_CATEGORY:
            self.abort(400)
        elif category == EVENT_CATEGORY:
            event = HistoryEvent.get_by_id(mark_id)
            if not event:
                self.abort(400)
            period = event.get_period()
        elif category == PERSON_CATEGORY:
            person = HistoryPerson.get_by_id(mark_id)
            if not person:
                self.abort(400)
            period = person.get_period()
        elif category == VIDEO_CATEGORY:
            video = YoutubeVideo.get_by_id(mark_id)
            if not video:
                self.abort(400)
            period = video.get_period()
        if period:
            self.render_json({
                'period_id': str(period.id())
            })
        else:
            self.abort(400)


class NewHistoryMarksHandler(ApiHandler):
    def get(self):
        def get_new_marks_info():
            info = memcache.get(key=MEM_CACHE_NEW_MARKS_KEY_MASK % country_id)
            if not info:
                events = HistoryEvent.get_new_marks(country, amount, timestamp)
                persons = HistoryPerson.get_new_marks(country, amount, timestamp)
                while (len(events) + len(persons)) > amount:
                    if len(events) == 0:
                        persons.remove(persons[len(persons) - 1])
                        break
                    if len(persons) == 0:
                        events.remove(events[len(events) - 1])
                        break
                    if events[len(events) - 1].created < persons[len(persons) - 1].created:
                        events.remove(events[len(events) - 1])
                    else:
                        persons.remove(persons[len(persons) - 1])
                info = {
                    'events': [event.dict() for event in events],
                    'persons': [person.dict() for person in persons],
                }
                memcache.add(key=MEM_CACHE_NEW_MARKS_KEY_MASK % country_id, value=info, time=MEM_CACHE_TIME)
            return info

        timestamp = self.request.get_range('timestamp')
        amount = self.request.get_range('amount')
        country_id = self.request.get_range('country_id')
        country = HistoryCountry.get_by_id(country_id)
        if not country:
            self.abort(400)
        if not timestamp:
            timestamp = mapping.timestamp(datetime.now() + timedelta(days=10))

        self.render_json(get_new_marks_info())
