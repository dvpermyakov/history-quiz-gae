import json

import logging
from webapp2 import RequestHandler
from models.user import WITHOUT_ID


class ApiHandler(RequestHandler):
    def dispatch(self):
        self.request.user_agent = self.request.headers.get("User-Agent")
        self.request.version = self.request.headers.get("Version")
        self.request.user_id = self.request.headers.get("User-Id")
        self.request.secret = self.request.headers.get("Secret")

        logging.info("Version = %s" % self.request.version)
        logging.info("User-Id = %s" % self.request.user_id)
        logging.info("Secret = %s" % self.request.secret)

        if self.with_id_user():
            self.request.user_id = int(self.request.user_id)
        return super(ApiHandler, self).dispatch()

    def with_id_user(self):
        return self.request.user_id and int(self.request.user_id) != WITHOUT_ID

    def forbidden_user(self):
        return self.with_id_user() and not self.request.secret

    def render_json(self, obj):
        self.response.headers["Content-Type"] = "application/json"
        self.response.write(json.dumps(obj))
