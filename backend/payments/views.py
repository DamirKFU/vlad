import django.db
import rest_framework.response
import rest_framework.status
import rest_framework.views

import catalog.models


class YooKassaWebhookView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request, *args, **kwargs):

        try:
            event_json = request.data
            order = catalog.models.Order.objects.get(
                payment_id=event_json["object"]["id"],
            )

            if event_json["event"] == "payment.succeeded":
                with django.db.transaction.atomic():
                    order.payment_status = (
                        catalog.models.PaymentStatus.SUCCEEDED
                    )
                    order.save()
                    order.status = catalog.models.OrderStatus.PAID
                    order.save()

            elif event_json["event"] == "payment.canceled":
                with django.db.transaction.atomic():
                    order.payment_status = (
                        catalog.models.PaymentStatus.CANCELED
                    )
                    order.save()
                    order.status = catalog.models.OrderStatus.CANCELED
                    order.save()

            return rest_framework.response.Response(
                {"status": "success"},
                status=rest_framework.status.HTTP_200_OK,
            )

        except Exception as e:
            return rest_framework.response.Response(
                {"error": str(e)},
                status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )
