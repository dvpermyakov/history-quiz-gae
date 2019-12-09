from google.appengine.api import memcache

from handlers.api.base import ApiHandler
from methods.strings import MEM_CACHE_VIDEO_INFO_KEY_MASK, MEM_CACHE_TIME
from models.video import YoutubeVideo


class VideoInfoHandler(ApiHandler):
    def get(self):
        def get_info():
            info = memcache.get(key=MEM_CACHE_VIDEO_INFO_KEY_MASK % video_id)
            if not info:
                video = YoutubeVideo.get_by_id(video_id)
                if not video:
                    self.abort(400)
                info = {
                    'test': video.test.get().dict() if video.test else None
                }
                memcache.add(key=MEM_CACHE_VIDEO_INFO_KEY_MASK % video_id, value=info, time=MEM_CACHE_TIME)
            return info
        
        video_id = self.request.get_range('video_id')
        if not video_id:
            self.abort(400)

        self.render_json(get_info())
