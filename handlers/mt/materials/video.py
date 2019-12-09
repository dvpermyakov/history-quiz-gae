from handlers.mt.base import MtHandler
from methods.mapping import sorted_history_marks
from methods.youtube import save_video_info
from models.history import HistoryEvent, HistoryPerson, MARK_CATEGORIES, PERSON_CATEGORY, EVENT_CATEGORY, \
    PERIOD_CATEGORY, HistoryPeriod
from models.test import Test
from models.video import YoutubeVideo


class VideoListHandler(MtHandler):
    def get(self):
        mark_id = self.request.get_range('mark_id')
        category = self.request.get_range('category')
        if category not in MARK_CATEGORIES:
            self.abort(400)
        videos = []
        back_link = ""
        add_link = "/mt/materials/videos/add?parent_mark_id=%s&parent_category=%s" % (mark_id, category)
        if category == PERSON_CATEGORY:
            person = HistoryPerson.get_by_id(mark_id)
            videos = sorted_history_marks(YoutubeVideo.get_by_mark(person))
            # back_link = "/mt/materials/periods/list"
        elif category == EVENT_CATEGORY:
            event = HistoryEvent.get_by_id(mark_id)
            videos = sorted_history_marks(YoutubeVideo.get_by_mark(event))
        self.render('/materials/video_list.html',
                    videos=videos,
                    back_link=back_link,
                    add_link=add_link)


class VideoAddHandler(MtHandler):
    def get(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')
        back_link = '/mt/materials/videos/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category)
        self.render('/materials/video_add.html',
                    back_link=back_link,
                    parent_mark_id=parent_mark_id, parent_category=parent_category)

    def post(self):
        parent_mark_id = self.request.get_range('parent_mark_id')
        parent_category = self.request.get_range('parent_category')

        test = Test()
        test.put()
        video = YoutubeVideo()

        if parent_category == PERSON_CATEGORY:
            person = HistoryPerson.get_by_id(parent_mark_id)
            video.person = person.key
        elif parent_category == EVENT_CATEGORY:
            event = HistoryEvent.get_by_id(parent_mark_id)
            video.event = event.key
        elif parent_category == PERIOD_CATEGORY:
            period = HistoryPeriod.get_by_id(parent_mark_id)
            video.period = period.key
        video.test = test.key
        video.youtube_id = self.request.get("youtube_id")
        video.title = self.request.get("title")
        video.shortcut = self.request.get("shortcut")
        video.sort_index = self.request.get_range("sort_index")
        video.put()

        save_video_info(video)

        self.redirect('/mt/materials/videos/list?mark_id=%s&category=%s' % (parent_mark_id, parent_category))
