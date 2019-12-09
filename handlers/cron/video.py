from webapp2 import RequestHandler

from methods.email import send_mail_to_admins
from methods.youtube import save_video_info
from models.video import YoutubeVideo


class VideosUpdateHandler(RequestHandler):
    def get(self):
        videos = YoutubeVideo.query().fetch()
        for video in videos:
            save_video_info(video)
        send_mail_to_admins("video", "Youtube video updates", "%s youtube videos were updated!" % len(videos))
