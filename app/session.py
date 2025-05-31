from flask.sessions import SecureCookieSessionInterface
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionMixin
import json

class CustomSession(CallbackDict, SessionMixin):
    pass

class CustomSessionInterface(SecureCookieSessionInterface):
    def open_session(self, app, request):
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        val = request.cookies.get('session')
        if not val:
            return CustomSession()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return CustomSession(data)
        except Exception:
            return CustomSession()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                response.delete_cookie('session',
                                    domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)
        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))
        response.set_cookie('session', val,
                          expires=expires, httponly=httponly,
                          domain=domain, path=path, secure=secure,
                          samesite=samesite) 