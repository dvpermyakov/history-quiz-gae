import logging

from handlers.api.base import ApiHandler
from models.user import User


class ApproveUserIdHandler(ApiHandler):
    def post(self):
        if self.with_id_user():
            if self.forbidden_user():
                self.abort(403)
            approve = User.get_user(self.request.user_id, self.request.secret) is not None
        else:
            approve = False
        self.render_json({
            'approved': approve
        })


class RegistrationUserHandler(ApiHandler):
    def post(self):
        user = User.create()
        user.user_agent = self.request.user_agent
        user.type = user.get_type()
        user.put()
        self.render_json(user.dict())


class SetUserInfoHandler(ApiHandler):
    def post(self):
        if self.with_id_user():
            if self.forbidden_user():
                self.abort(403)
            user = User.get_user(self.request.user_id, self.request.secret)
            if not user:
                self.abort(403)
            user.name = self.request.get('name')
            user.with_name = user.is_authorized()
            image = self.request.get('image')
            if image:
                user.image = image
            email = self.request.get('email')
            if email:
                user.email = email
            user.put()
            self.render_json({
                'success': True
            })
        else:
            self.abort(401)


class SetVKHandler(ApiHandler):
    def post(self):
        if self.with_id_user():
            if self.forbidden_user():
                self.abort(403)
            user = User.get_user(self.request.user_id, self.request.secret)
            if not user:
                self.abort(403)
            user.vk = self.request.get('vk')
            user.put()
            self.render_json({
                'success': True
            })
        else:
            self.abort(401)


class ListRatingHandler(ApiHandler):
    def get(self):
        users = User.query(User.with_name == True).order(-User.test_done_amount).order(User.attempts_amount).fetch(20)
        self.render_json({
            'users': [user.info_dict() for user in users],
        })
