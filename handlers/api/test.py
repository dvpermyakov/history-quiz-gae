from google.appengine.api import memcache

from handlers.api.base import ApiHandler
from methods.strings import MEM_CACHE_TEST_QUESTIONS_KEY_MASK, MEM_CACHE_TIME
from models.test import Test, TestDoneAction
from models.user import User


class TestQuestionsHandler(ApiHandler):
    def post(self):
        def get_questions():
            questions = memcache.get(key=MEM_CACHE_TEST_QUESTIONS_KEY_MASK % test_id)
            if not questions:
                test = Test.get_by_id(test_id)
                if test:
                    questions = test.get_questions_dicts()
                    memcache.add(key=MEM_CACHE_TEST_QUESTIONS_KEY_MASK % test_id, value=questions, time=MEM_CACHE_TIME)
            return questions

        test_id = self.request.get_range('test_id')
        if not test_id:
            self.abort(400)
        questions = get_questions()
        if questions is None:
            self.abort(400)
        self.render_json({
            'questions': questions,
        })


class TestDoneHandler(ApiHandler):
    def post(self):
        if self.with_id_user():
            if self.forbidden_user():
                self.abort(403)
            user = User.get_user(self.request.user_id, self.request.secret)
            if not user:
                self.abort(403)
            test_id = self.request.get_range('test_id')
            test = Test.get_by_id(test_id)
            if not test:
                self.abort(400)
            attempts = self.request.get_range('attempts')
            if attempts == 0:
                self.abort(422)
            test_done = TestDoneAction.query(TestDoneAction.user == user.key, TestDoneAction.test == test.key).fetch()
            if not test_done:
                test_done = TestDoneAction(user=user.key, test=test.key, attempts=attempts)
                test_done.put()
                user.update_test_done_amount()
            self.render_json({
                'success': True
            })
        else:
            self.abort(401)