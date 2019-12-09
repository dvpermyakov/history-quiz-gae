# coding=utf-8
from datetime import datetime, timedelta
from webapp2 import RequestHandler

from methods import email
from methods import vk
from models.test import TestDoneAction
from models.user import User, VKMessageSpam, VKAddToFriendAttempt

SEND_MESSAGE = "Добрый день!\nМы небольшой командой стараемся создать интересное и полезное приложение по истории России! Будем очень благодарны, если Вы вступите в нашу группу: https://vk.com/history_quiz\nПрошу прощения за небольшой спам :)"

MIN_TEST_DONE_AMOUNT = 3
MAX_TEST_DONE_AMOUNT = 50
LAST_ACTIVE_TEST_DONE = 10  # in days
MAX_SENDING_PER_DAY = 5
MAX_FAILURE_PER_DAY = 5

CAPTCHA_ERROR = 14


class SpamHandler(RequestHandler):
    @staticmethod
    def send_email(success, failure, captcha=False):
        text = "New spamming was done. Sending messages = %s, Failure sending = %s." % (success, failure)
        if captcha:
            text += " Additionally, problem with captcha!"
        email.send_mail_to_admins("spam", "vkontakte spamming", text)

    def get(self):
        sending_amount = 0
        failure_amount = 0
        users = User.query(User.vk != None).fetch()
        for user in users:
            if vk.is_group_member(user.vk):
                continue
            if user.test_done_amount < MIN_TEST_DONE_AMOUNT or user.test_done_amount > MAX_TEST_DONE_AMOUNT:
                continue
            last_test = TestDoneAction.query(TestDoneAction.user == user.key).order(-TestDoneAction.created).get()
            if last_test and last_test.created > datetime.now() - timedelta(days=LAST_ACTIVE_TEST_DONE):
                continue
            spam = VKMessageSpam.query(VKMessageSpam.user == user.key).fetch()
            if spam:
                continue
            spam = VKAddToFriendAttempt.query(VKAddToFriendAttempt.user == user.key).fetch()
            if spam:
                continue

            response = vk.send_message(user, SEND_MESSAGE)
            if response is not None:
                if not response.get('success') and response.get('code') == CAPTCHA_ERROR:
                    self.send_email(sending_amount, failure_amount, True)
                    return
                spam = VKMessageSpam()
                spam.user = user.key
                spam.success = response.get('success')
                spam.message = SEND_MESSAGE
                spam.response = response.get('code')
                spam.put()

                if response.get('success'):
                    sending_amount += 1
                else:
                    failure_amount += 1
            else:
                failure_amount += 1

            if sending_amount >= MAX_SENDING_PER_DAY or failure_amount >= MAX_FAILURE_PER_DAY:
                self.send_email(sending_amount, failure_amount)
                return
        self.send_email(sending_amount, failure_amount)
