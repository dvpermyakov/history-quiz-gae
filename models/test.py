import random

from google.appengine.ext import ndb

from models.user import User

MAX_QUESTIONS = 30


class Test(ndb.Model):
    max_questions = ndb.IntegerProperty(default=0)
    max_mistakes = ndb.IntegerProperty(default=0)
    max_seconds = ndb.IntegerProperty(default=0)

    def get_questions_dicts(self):
        return [question.dict_with_answers() for question in Question.query(Question.test == self.key).fetch(MAX_QUESTIONS)]

    def dict(self):
        return {
            'id': str(self.key.id()),
            'max_questions': self.max_questions,
            'max_mistakes': self.max_mistakes,
            'max_seconds': self.max_seconds,
        }


class Answer(ndb.Model):
    text = ndb.StringProperty(required=True)

    def dict(self):
        return {
            'id': str(self.key.id()),
            'text': self.text,
        }


class Question(ndb.Model):
    test = ndb.KeyProperty(kind=Test, repeated=True)
    text = ndb.StringProperty(required=True)
    correct = ndb.KeyProperty(required=True, kind=Answer)
    incorrect = ndb.KeyProperty(repeated=True, kind=Answer)

    @classmethod
    def get(cls, test):
        return

    def dict_with_answers(self):
        result = self.dict()
        correct_answer = self.correct.get().dict()
        correct_answer['correct'] = True
        answers = [answer.get().dict() for answer in self.incorrect]
        for answer in answers:
            answer['correct'] = False
        answers.append(correct_answer)
        random.shuffle(answers)
        result['answers'] = answers
        return result

    def dict(self):
        return {
            'id': str(self.key.id()),
            'text': self.text,
        }


class TestDoneAction(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.KeyProperty(required=True, kind=User)
    test = ndb.KeyProperty(required=True, kind=Test)
    attempts = ndb.IntegerProperty(required=True)
