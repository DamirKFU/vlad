import django.db
import rest_framework.response
import rest_framework.status
import rest_framework.views

import catalog.models
import core.utils


class YooKassaWebhookView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request, *args, **kwargs):

        try:
            event_json = request.data

            if event_json.get("type") != "notification":
                return core.utils.error_response(
                    message="Неверный тип уведомления",
                    http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
                )

            order = catalog.models.Order.objects.get_for_yookassa_webhook(
                payment_id=event_json["object"]["id"],
            )

            if not order:
                return core.utils.error_response(
                    message="Заказ не найден",
                    form_error="Заказ не найден",
                    http_status=rest_framework.status.HTTP_404_NOT_FOUND,
                )

            if event_json["event"] == "payment.succeeded":
                with django.db.transaction.atomic():
                    order.payment_status = (
                        catalog.models.PaymentStatus.SUCCEEDED
                    )
                    has_embroidery = any(
                        item.product.embroidery for item in order.items.all()
                    )
                    if not has_embroidery:
                        order.status = catalog.models.OrderStatus.PAID
                    else:
                        order.status = catalog.models.OrderStatus.IN_WORK

                    order.save(
                        update_fields=[
                            catalog.models.Order.payment_status.field.name,
                            catalog.models.Order.status.field.name,
                        ]
                    )

            elif event_json["event"] == "payment.canceled":
                with django.db.transaction.atomic():
                    order.payment_status = (
                        catalog.models.PaymentStatus.CANCELED
                    )
                    order.status = catalog.models.OrderStatus.CANCELED
                    order.save(
                        update_fields=[
                            catalog.models.Order.payment_status.field.name,
                            catalog.models.Order.status.field.name,
                        ]
                    )
            else:
                return core.utils.error_response(
                    message="Неизвестный тип события",
                    http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
                )

            return core.utils.success_response(
                message="Webhook успешно обработан",
            )

        except Exception as e:
            return core.utils.error_response(
                message="Ошибка обработки webhook",
                fields={"form_error": str(e)},
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )
