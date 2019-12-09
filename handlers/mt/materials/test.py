from handlers.mt.base import MtHandler
from models.history import MARK_CATEGORIES, PERIOD_CATEGORY, EVENT_CATEGORY, PERSON_CATEGORY
from models.test import Test, Question, Answer


class TestListHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        out_category = self.request.get_range('out_category')
        test_id = self.request.get_range('test_id')
        test = Test.get_by_id(test_id)
        if not test:
            self.abort(400)
        if out_category not in MARK_CATEGORIES:
            self.abort(400)
        if out_category == PERIOD_CATEGORY:
            back_link = "/mt/materials/periods/list"
        elif out_category == EVENT_CATEGORY:
            back_link = '/mt/materials/events/list?mark_id=%s&category=%s' % (mark_id, category)
        elif out_category == PERSON_CATEGORY:
            back_link = '/mt/materials/persons/list?mark_id=%s&category=%s' % (mark_id, category)
        add_link = '/mt/materials/test/question/add?mark_id=%s&category=%s&test_id=%s' % (mark_id, category, test.key.id())
        change_link = '/mt/materials/test/change?parent_mark_id=%s&parent_category=%s&test_id=%s' % (mark_id, category, test.key.id())
        test.questions = Question.query(Question.test == test.key).fetch()
        for question in test.questions:
            question.correct_obj = question.correct.get()
            question.incorrect_obj = [incorrect.get() for incorrect in question.incorrect]
            question.change_link = '/mt/materials/test/question/change?mark_id=%s&category=%s&question_id=%s' % (mark_id, category, question.key.id())
        self.render('/materials/test_list.html',
                    test=test,
                    change_link=change_link,
                    back_link=back_link,
                    add_link=add_link)


class TestChangeHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        test_id = self.request.get_range('test_id')
        test = Test.get_by_id(test_id)
        if not test:
            self.abort(400)
        back_link = '/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (parent_mark_id, parent_category, test_id)
        self.render('/materials/test_change.html',
                    test=test,
                    back_link=back_link)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        test_id = self.request.get_range('test_id')
        test = Test.get_by_id(test_id)
        if not test:
            self.abort(400)
        test.max_questions = self.request.get_range('max_questions')
        test.max_mistakes = self.request.get_range('max_mistakes')
        test.max_seconds = self.request.get_range('max_seconds')
        test.put()
        self.redirect('/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (parent_mark_id, parent_category, test_id))


class QuestionChangeHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        question_id = self.request.get_range('question_id')
        question = Question.get_by_id(question_id)
        if not question:
            self.abort(400)
        question.correct_obj = question.correct.get()
        question.incorrect_obj = [incorrect.get() for incorrect in question.incorrect]
        add_link = '/mt/materials/test/answer/add?mark_id=%s&category=%s&question_id=%s' % (mark_id, category, question.key.id())
        back_link = '/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (mark_id, category, question.test[0].id())
        self.render('/materials/question_change.html',
                    question=question,
                    back_link=back_link,
                    add_link=add_link)

    def post(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        question_id = self.request.get_range('question_id')
        question = Question.get_by_id(question_id)
        if not question:
            self.abort(400)
        question.text = self.request.get('text')
        answer = question.correct.get()
        answer.text = self.request.get('correct')
        answer.put()
        question.put()
        for index, answer in enumerate(question.incorrect):
            answer = answer.get()
            answer.text = self.request.get('correct_%s' % index)
            answer.put()
        self.redirect('/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (mark_id, category, question.test[0].id()))


class QuestionAddHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        test_id = self.request.get_range('test_id')
        test = Test.get_by_id(test_id)
        if not test:
            self.abort(400)
        back_link = '/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (mark_id, category, test.key.id())
        self.render('/materials/question_add.html',
                    test=test,
                    back_link=back_link)

    def post(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        test_id = self.request.get_range('test_id')
        test = Test.get_by_id(test_id)
        if not test:
            self.abort(400)
        question = Question()
        question.test = [test.key]
        question.text = self.request.get('text')
        answer = Answer()
        answer.text = self.request.get('answer')
        answer.put()
        question.correct = answer.key
        question.put()
        self.redirect('/mt/materials/test/list?mark_id=%s&category=%s&test_id=%s' % (mark_id, category, test.key.id()))


class AnswerAddHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        question_id = self.request.get_range('question_id')
        question = Question.get_by_id(question_id)
        if not question:
            self.abort(400)
        back_link = '/mt/materials/test/question/change?mark_id=%s&category=%s&question_id=%s' % (mark_id, category, question.key.id())
        self.render('/materials/answer_add.html',
                    question=question,
                    back_link=back_link)

    def post(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        question_id = self.request.get_range('question_id')
        question = Question.get_by_id(question_id)
        if not question:
            self.abort(400)
        answer = Answer()
        answer.text = self.request.get('text')
        answer.put()
        question.incorrect.append(answer.key)
        question.put()
        self.redirect('/mt/materials/test/question/change?mark_id=%s&category=%s&question_id=%s' % (mark_id, category, question.key.id()))
