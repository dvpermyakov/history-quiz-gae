# coding=utf-8
import json
import urllib
import logging

from google.appengine.api import urlfetch

BASE_URL = 'http://speller.yandex.net/services/spellservice.json/'


def check_text(text):
    url = '%s%s?%s' % (BASE_URL, 'checkText', urllib.urlencode({
        'text': text.encode('utf-8'),
        'options': 0,
        'lang': 'ru',
        'format': 'plain',
    }))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    return response

