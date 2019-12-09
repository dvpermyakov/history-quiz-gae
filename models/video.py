from google.appengine.ext import ndb

from methods.mapping import add_thousands_spaces
from models.history import HistoryPeriod, HistoryEvent, HistoryPerson, PERSON_CATEGORY, EVENT_CATEGORY, PERIOD_CATEGORY
from models.test import Test


class YoutubeChannel(ndb.Model):
    channel_id = ndb.StringProperty(required=True)
    title = ndb.StringProperty()
    icon = ndb.StringProperty()
    subscriber_count = ndb.IntegerProperty()
    video_count = ndb.IntegerProperty()

    @classmethod
    def get_by_channel_id(cls, channel_id):
        channels = cls.query(cls.channel_id == channel_id).fetch()
        if len(channels) > 0:
            return channels[0]
        else:
            return None

    def dict(self):
        return {
            'id': str(self.channel_id),
            'title': self.title,
            'icon': self.icon,
            'subscriber_count': add_thousands_spaces(str(self.subscriber_count)),
            'video_count': add_thousands_spaces(str(self.video_count)),
        }


class YoutubeVideo(ndb.Model):
    period = ndb.KeyProperty(kind=HistoryPeriod)  # only one is not None
    event = ndb.KeyProperty(kind=HistoryEvent)    # only one is not None
    person = ndb.KeyProperty(kind=HistoryPerson)  # only one is not None
    sort_index = ndb.IntegerProperty(default=0)
    test = ndb.KeyProperty(kind=Test)
    embeddable = ndb.BooleanProperty()

    youtube_id = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    shortcut = ndb.StringProperty()
    channel_id = ndb.StringProperty()
    icon = ndb.StringProperty()
    duration = ndb.StringProperty()
    view_count = ndb.IntegerProperty(default=0)
    like_count = ndb.IntegerProperty(default=0)
    comment_count = ndb.IntegerProperty(default=0)

    @classmethod
    def get_by_mark(cls, mark):
        if mark.category == PERSON_CATEGORY:
            return cls.query(cls.person == mark.key).fetch()
        elif mark.category == EVENT_CATEGORY:
            return cls.query(cls.event == mark.key).fetch()
        elif mark.category == PERIOD_CATEGORY:
            return cls.query(cls.period == mark.key).fetch()
        return []

    def get_period(self):
        mark = self
        while mark.period is None:
            if mark.person:
                mark = mark.person.get()
            elif mark.event:
                mark = mark.event.get()
        if mark.period:
            return mark.period
        return None

    def get_count(self):
        return 1 if self.test.get().max_questions > 0 else 0

    def dict(self):
        return {
            'id': str(self.key.id()),
            'youtube_id': self.youtube_id,
            'url': 'https://www.youtube.com/watch?v=%s' % self.youtube_id,
            'embeddable': self.embeddable,
            'title': self.title,               # deprecated
            'icon':  self.icon,                # deprecated
            'name': self.title,                # duplicated
            'image':  self.icon,               # duplicated
            'shortcut': self.shortcut,
            'channel_id': self.channel_id,
            'duration': self.duration,
            'view_count': add_thousands_spaces(str(self.view_count)),
            'like_count': add_thousands_spaces(str(self.like_count)),
            'comment_count': add_thousands_spaces(str(self.comment_count)),
        }
