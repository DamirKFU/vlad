import celery
import django.db

import catalog.models


@celery.shared_task(bind=True)
@django.db.transaction.atomic
def create_order_task(self, data, user_id):
    serializer = catalog.serializers.CreateOrderSerializer(
        data=data, context={"user_id": user_id}
    )
    if not serializer.is_valid():
        self.update_state(
            state="FAILURE",
            meta={},
        )
        return {
            "message": "Ошибка валидации",
            "errors": serializer.errors,
        }

    order = serializer.save()
    self.update_state(
        state="SUCCESS",
        meta={"order_id": order.id},
    )
    return {
        "data": {"order_id": order.id},
        "message": "Заказ успешно создан",
    }
