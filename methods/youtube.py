import json
import logging
import urllib

from google.appengine.api import urlfetch

from methods.mapping import get_date_from_youtube, to_app_duration_format
from models.video import YoutubeChannel

YOUTUBE_API_KEY = "AIzaSyA7BVtq3hGlSKFb2tsF5ORgL3aQV_5w1D0"
BASE_URL = 'https://www.googleapis.com/youtube/v3/'


def _send(category, params):
    params['key'] = YOUTUBE_API_KEY
    url = '%s%s?%s' % (BASE_URL, category, urllib.urlencode(params))
    logging.info(url)
    try:
        response = urlfetch.fetch(url, deadline=3)
        response = json.loads(response.content)
    except Exception as e:
        logging.info(str(e))
        response = None
    if response and response.get('items') and len(response.get('items')) > 0:
        return response['items'][0]
    else:
        return None


def save_video_info(video):
    description = _send('videos', {
        'part': 'snippet,statistics,contentDetails,status',
        'id': video.youtube_id
    })
    if description:
        video.embeddable = description['status']['embeddable']
        video.channel_id = description['snippet']['channelId']
        if description['snippet']['thumbnails'].get('standard'):
            video.icon = description['snippet']['thumbnails']['standard']['url']
        else:
            video.icon = description['snippet']['thumbnails']['high']['url']
        video.duration = to_app_duration_format(get_date_from_youtube(description['contentDetails']['duration']))
        video.view_count = int(description['statistics']['viewCount'])
        video.like_count = int(description['statistics']['likeCount'])
        video.comment_count = int(description['statistics']['commentCount'])
        video.put()
        channels = YoutubeChannel.query(YoutubeChannel.channel_id == video.channel_id).fetch()
        if len(channels) > 0:
            channel = channels[0]
        else:
            channel = YoutubeChannel(channel_id=video.channel_id)
        channel.title = description['snippet']['channelTitle']
        channel.put()
        save_channel_info(channel)


def save_channel_info(channel):
    description = _send('channels', {
        'part': 'id,snippet,statistics',
        'id': channel.channel_id
    })
    if description:
        channel.title = description['snippet']['title']
        channel.icon = description['snippet']['thumbnails']['high']['url']
        channel.subscriber_count = int(description['statistics']['subscriberCount'])
        channel.video_count = int(description['statistics']['videoCount'])
        channel.put()
