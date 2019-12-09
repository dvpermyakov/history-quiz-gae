from google.appengine.ext import deferred
from webapp2 import RequestHandler

from methods import email
from methods import speller
from models.history import HistoryEvent, HistoryPerson


class CheckMarkSpellingHandler(RequestHandler):
    def get(self):
        for mark in HistoryPerson.query().fetch():
            deferred.defer(search_mistake, mark.name, mark.text.get())


def search_mistake(mark_name, text):
    body = ""
    for index, p in enumerate(text.paragraphs):
        response = speller.check_text(p.text)
        if response:
            for mistake in response:
                code = mistake['code']
                word = mistake['word']
                error = ', '.join(mistake['error']) if mistake.get('error') else 'empty'
                hint = ', '.join(mistake['s']) if mistake.get('s') else 'empty'
                body += 'Paragraph (%s):\nMistake code (%s) for word %s with error(%s) and hints (%s)\n\n' % (
                index, code, word, error, hint)
    if body:
        body = 'For mark %s:\n\n' % mark_name + body
        email.send_mail_to_admins("spelling", "Periods spelling mistakes", body)
