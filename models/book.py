from google.appengine.ext import ndb

from models.history import HistoryEvent, PERSON_CATEGORY, EVENT_CATEGORY, PERIOD_CATEGORY
from models.history import HistoryPeriod
from models.history import HistoryPerson
from models.test import Test


class Author(ndb.Model):
    name = ndb.StringProperty(required=True)
    start = ndb.DateProperty(required=True)
    end = ndb.DateProperty(required=True)

    def dict(self):
        from methods.mapping import get_year_title
        return {
            'id': str(self.key.id()),
            'name': self.name,
            'year_title': get_year_title(self.start, self.end),
        }


class Book(ndb.Model):
    period = ndb.KeyProperty(kind=HistoryPeriod)  # only one is not None
    event = ndb.KeyProperty(kind=HistoryEvent)    # only one is not None
    person = ndb.KeyProperty(kind=HistoryPerson)  # only one is not None
    sort_index = ndb.IntegerProperty(default=0)
    test = ndb.KeyProperty(kind=Test)

    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    image = ndb.StringProperty(required=True)
    author = ndb.KeyProperty(kind=Author, required=True)

    @classmethod
    def get_by_mark(cls, mark):
        if mark.category == PERSON_CATEGORY:
            return cls.query(cls.person == mark.key).fetch()
        elif mark.category == EVENT_CATEGORY:
            return cls.query(cls.event == mark.key).fetch()
        elif mark.category == PERIOD_CATEGORY:
            return cls.query(cls.period == mark.key).fetch()
        return []

    def dict(self):
        return {
            'id': str(self.key.id()),
            'name': self.name,
            'url': self.url,
            'image': self.image,
            'author': self.author.get().dict()
        }
