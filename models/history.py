# coding=utf-8
from google.appengine.ext import ndb

from methods.strings import DEFAULT_GROUP_TITLE
from models.test import Test
from models.text import Text

PERIOD_CATEGORY = 0
EVENT_CATEGORY = 1
PERSON_CATEGORY = 2
VIDEO_CATEGORY = 3
MARK_CATEGORIES = (PERIOD_CATEGORY, EVENT_CATEGORY, PERSON_CATEGORY, VIDEO_CATEGORY)


class HistoryCountry(ndb.Model):
    updated = ndb.DateTimeProperty(auto_now=True)
    name = ndb.StringProperty(required=True)

    def update(self):
        for period in HistoryPeriod.query(HistoryPeriod.country == self.key).fetch():
            period.update_count()
        self.put()

    def dict(self):
        return {
            'id': str(self.key.id()),
            'name': self.name
        }


class HistoryMark(ndb.Model):
    created = ndb.DateProperty(auto_now_add=True)
    updated = ndb.DateProperty(auto_now=True)
    sort_index = ndb.IntegerProperty(default=0)

    category = ndb.IntegerProperty()
    available = ndb.BooleanProperty(default=False)
    name = ndb.StringProperty(required=True)
    start = ndb.DateProperty(required=True)
    end = ndb.DateProperty(required=True)
    image = ndb.StringProperty(default="")
    description = ndb.StringProperty(default="")
    text = ndb.KeyProperty(kind=Text)
    test = ndb.KeyProperty(kind=Test)

    country = ndb.KeyProperty(required=True, kind=HistoryCountry)
    period = ndb.KeyProperty()  # kind=HistoryPeriod  ## parent
    event = ndb.KeyProperty()   # kind=HistoryEvent   ## parent
    person = ndb.KeyProperty()  # kind=HistoryPerson  ## parent

    group_title = ndb.StringProperty(default=DEFAULT_GROUP_TITLE)
    dependencies = ndb.KeyProperty(repeated=True)  # kind=self

    @classmethod
    def get_new_marks(cls, country, amount, timestamp):
        return cls.query(cls.country == country.key,
                         #cls.created < datetime.fromtimestamp(timestamp),
                         cls.available == True).order(-cls.created).fetch(amount)

    @classmethod
    def get_by_mark(cls, mark, consider_avail=True):
        if mark.category == PERSON_CATEGORY:
            return cls.get_by_person(mark, consider_avail)
        elif mark.category == EVENT_CATEGORY:
            return cls.get_by_event(mark, consider_avail)
        elif mark.category == PERIOD_CATEGORY:
            res = cls.get_by_period(mark, consider_avail)
            return res

    @classmethod
    def get_by_period(cls, period, consider_avail=True):
        response = []
        for mark in cls.query(cls.period == period.key).fetch():
            if not consider_avail or mark.available:
                response.append(mark)
        return response

    @classmethod
    def get_by_event(cls, event, consider_avail=True):
        response = []
        for mark in cls.query(cls.event == event.key).fetch():
            if not consider_avail or mark.available:
                response.append(mark)
        return response

    @classmethod
    def get_by_person(cls, person, consider_avail=True):
        response = []
        for mark in cls.query(cls.person == person.key).fetch():
            if not consider_avail or mark.available:
                response.append(mark)
        return response

    def get_count(self):
        from models.video import YoutubeVideo
        result = 1 if self.test.get().max_questions > 0 else 0
        result += sum(mark.get_count() for mark in HistoryPerson.get_by_mark(self))
        result += sum(mark.get_count() for mark in HistoryEvent.get_by_mark(self))
        result += sum(video.get_count() for video in YoutubeVideo.get_by_mark(self))
        return result

    def get_period(self):
        if self.category == PERIOD_CATEGORY:
            return self
        mark = self
        while mark.period is None:
            if mark.person:
                mark = mark.person.get()
            elif mark.event:
                mark = mark.event.get()
        if mark.period:
            return mark.period
        return None

    def dict(self):
        from methods.mapping import get_year_title, timestamp
        return {
            'id': str(self.key.id()),
            'category': str(self.category),
            'created': str(timestamp(self.created)),
            'name': self.name,
            'image': self.image,
            'description': self.description,
            'group_title': self.group_title,
            'year_title': get_year_title(self.start, self.end),
        }


class HistoryPeriod(HistoryMark):
    developing = ndb.BooleanProperty(default=True)
    count = ndb.IntegerProperty(default=0)

    def update_count(self):
        self.count = self.get_count() if not self.developing else 0
        self.put()

    def dict(self):
        result = super(HistoryPeriod, self).dict()
        result['developing'] = self.developing
        result['count'] = self.count
        return result


class HistoryEvent(HistoryMark):
    def dict(self):
        result = super(HistoryEvent, self).dict()
        return result


class HistoryPersonTitle(ndb.Model):
    name = ndb.StringProperty(required=True)
    start = ndb.DateProperty(required=True)
    end = ndb.DateProperty(required=True)

    def dict(self):
        from methods.mapping import get_year_title

        return {
            'name': self.name,
            'year_title': get_year_title(self.start, self.end)
        }


class HistoryPerson(HistoryMark):
    person_titles = ndb.StructuredProperty(HistoryPersonTitle, repeated=True)

    def dict(self):
        from methods.mapping import get_person_year_title

        result = super(HistoryPerson, self).dict()
        result['year_title'] = get_person_year_title(self.start, self.end)
        result['person_titles'] = [title.dict() for title in self.person_titles]
        return result
