import django.utils.deprecation

import users.logs


class EnsureSessionKeyMiddleware(django.utils.deprecation.MiddlewareMixin):
    def process_request(self, request):
        if request.session.session_key is None:
            request.session.create()
            users.logs.log_user_event("user_first_visit", request)
