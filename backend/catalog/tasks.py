import celery
import django.db
import django.utils

import catalog.serializers


def create_order_task_sync(self, data, user_id):
    serializer = catalog.serializers.CreateOrderSerializer(
        data=data, context={"user_id": user_id}
    )
    if not serializer.is_valid():
        return {
            "message": "Ошибка валидации",
            "errors": serializer.errors,
        }

    try:
        order = serializer.save()
    except django.db.utils.Error as exc:
        django.db.transaction.set_rollback(True)
        return {
            "message": "Ошибка создания заказа",
            "errors": {"form_error": str(exc)},
        }

    return {
        "data": {"order_id": order.id},
        "message": "Заказ успешно создан",
    }


@celery.shared_task(bind=True)
@django.db.transaction.atomic
def create_order_task(self, data, user_id):
    result = create_order_task_sync(self, data, user_id)

    if "errors" in result:
        self.update_state(state="FAILURE", meta=result)
        return result

    self.update_state(
        state="SUCCESS",
        meta={"order_id": result["data"]["order_id"]},
    )
    return result
