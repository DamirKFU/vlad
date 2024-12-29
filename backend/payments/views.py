import django.db
import rest_framework.response
import rest_framework.status
import rest_framework.views

import catalog.models
import payments.models


class YooKassaWebhookView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request, *args, **kwargs):

        try:
            event_json = request.data
            payment = payments.models.Payment.objects.select_related(
                "order"
            ).get(payment_id=event_json["object"]["id"])

            if event_json["event"] == "payment.succeeded":
                with django.db.transaction.atomic():
                    payment.status = payments.models.PaymentStatus.SUCCEEDED
                    payment.save()
                    payment.order.status = catalog.models.OrderStatus.PAID
                    payment.order.save()

            elif event_json["event"] == "payment.canceled":
                with django.db.transaction.atomic():
                    payment.status = payments.models.PaymentStatus.CANCELED
                    payment.save()
                    payment.order.status = catalog.models.OrderStatus.CANCELED
                    payment.order.save()

            return rest_framework.response.Response(
                {"status": "success"},
                status=rest_framework.status.HTTP_200_OK,
            )

        except Exception as e:
            return rest_framework.response.Response(
                {"error": str(e)},
                status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )
