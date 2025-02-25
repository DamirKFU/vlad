import celery
import celery.states
import celery_once
import django.db
import django.utils

import catalog.models
import catalog.serializers
import payments.services


@django.db.transaction.atomic
def create_order_task_sync(self, data, user_id):
    serializer = catalog.serializers.CreateOrderSerializer(
        data=data, context={"user_id": user_id}
    )
    if not serializer.is_valid():
        return {
            "message": "Ошибка валидации",
            "status": "error",
            "serializer_errors": serializer.errors,
        }

    order = serializer.save()

    return {
        "data": {"order_id": order.id},
        "status": "success",
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


@celery.shared_task(
    bind=True,
)
@django.db.transaction.atomic
def cancel_order_task(self, order_id, user_id):
    order = catalog.models.Order.objects.filter(
        user=user_id,
        id=order_id,
    ).first()

    if not order:
        return {
            "status": "error",
            "message": "Заказ не найден",
        }

    yookassa_service = payments.services.YooKassaService()
    status_payment = yookassa_service.get_status_payment(order.payment_id)
    if (
        order.status == catalog.models.OrderStatus.WAITING_PAYMENT
        and status_payment == catalog.models.PaymentStatus.SUCCEEDED
    ):
        order.status = catalog.models.OrderStatus.IN_WORK
        order.save(update_fields=[catalog.models.Order.status.field.name])
        return {
            "status": "error",
            "message": "Заказ оплачен, не может быть отменен",
        }

    try:
        order.cancel_order()
    except django.core.exceptions.ValidationError as e:
        return {
            "status": "error",
            "message": str(e.message),
        }

    return {
        "status": "success",
        "message": "Заказ успешно отменен",
    }
