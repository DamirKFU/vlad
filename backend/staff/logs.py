import datetime
import logging

import pytz

logger = logging.getLogger("grafana")


def log_order_status_change(
    order, user, old_status, new_status, error_comment=None
):
    logger.info(
        "Order status changed",
        extra={
            "order_id": order.id,
            "log_type": "order_status_change",
            "username": user.username if user else "system",
            "from_status": old_status,
            "to_status": new_status,
            "error_comment": error_comment,
            "timestamp": datetime.datetime.now(pytz.UTC).isoformat(),
        },
    )
