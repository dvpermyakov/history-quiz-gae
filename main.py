from webapp2 import WSGIApplication, Route
from webapp2_extras import jinja2
from webapp2_extras.routes import PathPrefixRoute

from handlers import api
from handlers.mt import materials

app = WSGIApplication([
    PathPrefixRoute('/mt', [
        PathPrefixRoute('/materials', [
            PathPrefixRoute('/countries', [
                Route('/list', materials.CountryListHandler),
                Route('/add', materials.CountryAddHandler),
            ]),
            PathPrefixRoute('/periods', [
                Route('/list', materials.HistoryPeriodListHandler),
                Route('/add', materials.HistoryPeriodAddHandler),
                Route('/change', materials.HistoryPeriodChangeHandler),
            ]),
            PathPrefixRoute('/events', [
                Route('/list', materials.HistoryEventListHandler),
                Route('/add', materials.HistoryEventAddHandler),
                Route('/change', materials.HistoryEventChangeHandler),
            ]),
            PathPrefixRoute('/persons', [
                Route('/list', materials.HistoryPersonListHandler),
                Route('/add', materials.HistoryPersonAddHandler),
                Route('/change', materials.HistoryPersonChangeHandler),
                PathPrefixRoute('/titles', [
                    Route('/list', materials.HistoryPersonTitleListHandler),
                    Route('/add', materials.HistoryPersonTitleAddHandler),
                    Route('/change', materials.HistoryPersonTitleChangeHandler),
                ]),
            ]),
            PathPrefixRoute('/videos', [
                Route('/list', materials.VideoListHandler),
                Route('/add', materials.VideoAddHandler),
            ]),
            PathPrefixRoute('/text', [
                Route('/list', materials.TextListHandler),
                Route('/add', materials.TextAddHandler),
                Route('/change', materials.TextChangeHandler),
            ]),
            PathPrefixRoute('/test', [
                Route('/list', materials.TestListHandler),
                Route('/change', materials.TestChangeHandler),
                PathPrefixRoute('/question', [
                    Route('/add', materials.QuestionAddHandler),
                    Route('/change', materials.QuestionChangeHandler),
                ]),
                PathPrefixRoute('/answer', [
                    Route('/add', materials.AnswerAddHandler),
                ]),
            ]),
            PathPrefixRoute('/dependency', [
                Route('/add', materials.DependencyAddHandler),
            ]),
        ]),
    ]),

    PathPrefixRoute('/api', [
        PathPrefixRoute('/user', [
            Route('/approve', api.ApproveUserIdHandler),
            Route('/register', api.RegistrationUserHandler),
            Route('/set_info', api.SetUserInfoHandler),
            Route('/set_vk', api.SetVKHandler),
        ]),

        PathPrefixRoute('/rating', [
            Route('/list', api.ListRatingHandler),
        ]),

        PathPrefixRoute('/video', [
            Route('/info', api.VideoInfoHandler),
        ]),

        PathPrefixRoute('/test', [
            Route('/questions', api.TestQuestionsHandler),
            Route('/done', api.TestDoneHandler),
        ]),

        PathPrefixRoute('/history', [
            PathPrefixRoute('/timestamp', [
                Route('/periods', api.TimestampHistoryPeriodsHandler),
            ]),
            Route('/periods', api.HistoryPeriodsHandler),
            Route('/mark_info', api.HistoryMarkInfoHandler),
            Route('/short_mark_info', api.ShortHistoryMarkInfoHandler),
            Route('/period_of_mark_info', api.PeriodOfMarkInfoHandler),
            Route('/new', api.NewHistoryMarksHandler),
        ]),
    ]),
])

jinja2.set_jinja2(jinja2.Jinja2(app), app=app)
