# coding=utf-8
from google.appengine.ext import ndb
from webapp2_extras import security

WITHOUT_ID = -1

UNKNOWN_USER = -1
ANDROID_APP_USER = 0
USER_TYPES = (UNKNOWN_USER, ANDROID_APP_USER)

DEFAULT_RUSSIAN_NAME = "Пользователь"


class User(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    secret = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True, choices=USER_TYPES)
    user_agent = ndb.StringProperty(required=True)
    name = ndb.StringProperty()
    with_name = ndb.BooleanProperty(default=False)
    image = ndb.StringProperty()
    email = ndb.StringProperty()
    vk = ndb.StringProperty()
    test_done_amount = ndb.IntegerProperty(default=0)
    attempts_amount = ndb.IntegerProperty(default=0)

    @classmethod
    def create(cls):
        return cls(secret=security.generate_random_string(entropy=256))

    @classmethod
    def get_user(cls, user_id, secret):
        user = cls.get_by_id(user_id)
        if not user:
            return None
        if user.secret == secret:
            return user
        else:
            return None

    def get_type(self):
        if 'Android' in self.user_agent:
            return ANDROID_APP_USER
        else:
            return UNKNOWN_USER

    def is_authorized(self):
        return self.name is not None and self.name.encode('utf8') != DEFAULT_RUSSIAN_NAME

    def update_test_done_amount(self):
        from models.test import TestDoneAction
        actions = TestDoneAction.query(TestDoneAction.user == self.key).fetch()
        self.test_done_amount = len(actions)
        self.attempts_amount = sum(action.attempts for action in actions)
        self.put()

    def info_dict(self):
        return {
            'id': str(self.key.id()),
            'name': self.name,
            'image': self.image,
            'test_done_amount': self.test_done_amount,
            'attempts_amount': self.attempts_amount,
        }

    def dict(self):
        return {
            'id': str(self.key.id()),
            'secret': self.secret,
        }


class VKAddToFriendAttempt(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    success = ndb.BooleanProperty()
    message = ndb.StringProperty(required=True)
    response = ndb.IntegerProperty(required=True)


class VKMessageSpam(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    success = ndb.BooleanProperty()
    message = ndb.StringProperty(required=True)
    response = ndb.IntegerProperty(required=True)
