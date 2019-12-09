import json
import logging
import urllib

from google.appengine.api import urlfetch

#URL_FETCH_ACCESS_TOKEN = 'http://oauth.vk.com/oauth/authorize?redirect_uri=http://oauth.vk.com/blank.html&response_type=token&client_id=5674042&scope=friends,messages,offline,group'

VK_GROUP_ID = '130401175'
VK_ACCESS_TOKEN = '1e0adc24971624e25bad3cd55f429fc40830e1f6c0c5a491d202da1cc9f88a2b5e26bdf6bc1d212bb7617'

BASE_URL = 'https://api.vk.com/method/'


# it returns only 1000 members
def get_group_member():
    url = '%s%s?%s' % (BASE_URL, 'groups.getMembers', urllib.urlencode({
        'group_id': VK_GROUP_ID,
        'access_token': VK_ACCESS_TOKEN,
    }))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    logging.info(response)
    if response and response.get('response'):
        return response['response']['users']
    else:
        return None


def is_group_member(user_id):
    url = '%s%s?%s' % (BASE_URL, 'groups.isMember', urllib.urlencode({
        'group_id': VK_GROUP_ID,
        'user_id': user_id,
    }))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    logging.info(response)
    if response and response.get('response') is not None:
        return response['response'] == 1
    else:
        return True


def add_friend(user, message):
    url = '%s%s?%s' % (BASE_URL, 'friends.add', urllib.urlencode({
        'user_id': user.vk,
        'text': message,
        'follow': 0,
        'access_token': VK_ACCESS_TOKEN
    }))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    logging.info(response)
    if response and response.get('response'):
        return {
            'success': True,
            'code': response['response'],
        }
    elif response and response.get('error'):
        return {
            'success': False,
            'code': response['error']['error_code']
        }
    else:
        return None


def send_message(user, message):
    url = '%s%s?%s' % (BASE_URL, 'messages.send',  urllib.urlencode({
        'user_id': user.vk,
        'message': message,
        'access_token': VK_ACCESS_TOKEN
    }))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    logging.info(response)
    if response and response.get('response'):
        return {
            'success': True,
            'code': response['response'],
        }
    elif response and response.get('error'):
        return {
            'success': False,
            'code': response['error']['error_code']
        }
    else:
        return None
