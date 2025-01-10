import datetime
import logging

import pytz

logger = logging.getLogger("grafana")


def log_user_event(event, request):
    if request.user.is_authenticated:
        logger.info(
            "User event",
            extra={
                "user_id": request.user.id,
                "log_type": "user_event",
                "username": request.user.username,
                "event": event,
                "timestamp": datetime.datetime.now(pytz.UTC).isoformat(),
            },
        )
    else:
        logger.info(
            "Anonymous user event",
            extra={
                "log_type": "anonymous_user_event",
                "session_id": request.session.session_key,
                "event": event,
                "timestamp": datetime.datetime.now(pytz.UTC).isoformat(),
            },
        )
