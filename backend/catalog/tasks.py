import celery
import celery.states
import celery_once
import django.db
import django.utils

import catalog.serializers


@django.db.transaction.atomic
def create_order_task_sync(self, data, user_id):
    serializer = catalog.serializers.CreateOrderSerializer(
        data=data, context={"user_id": user_id}
    )
    if not serializer.is_valid():
        return {
            "message": "Ошибка валидации",
            "serializer_errors": serializer.errors,
        }

    order = serializer.save()

    return {
        "data": {"order_id": order.id},
        "message": "Заказ успешно создан",
    }


@celery.shared_task(
    bind=True,
    base=celery_once.QueueOnce,
    once={"keys": ["user_id"]},
)
def create_order_task(self, data, user_id):
    try:
        return create_order_task_sync(self, data, user_id)
    except Exception as e:
        self.clear_lock()
        raise e
