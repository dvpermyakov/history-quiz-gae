from webapp2 import WSGIApplication, Route
from webapp2_extras.routes import PathPrefixRoute

from handlers.cron.social import SpamHandler
from handlers.cron.spelling import CheckMarkSpellingHandler
from handlers.cron.video import VideosUpdateHandler

app = WSGIApplication([
    PathPrefixRoute('/cron', [
        PathPrefixRoute('/video', [
            Route('/update', VideosUpdateHandler),
        ]),
        PathPrefixRoute('/social', [
            Route('/spam', SpamHandler),
        ]),
        # PathPrefixRoute('/spelling', [
        #     Route('/marks', CheckMarkSpellingHandler),
        # ]),
    ]),
])
