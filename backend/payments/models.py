import django.db.models
import django.utils.timezone

import catalog.models


class PaymentStatus(django.db.models.TextChoices):
    PENDING = "pending", "В ожидании"
    SUCCEEDED = "succeeded", "Успешно"
    CANCELED = "canceled", "Отменён"


class Payment(django.db.models.Model):
    order = django.db.models.OneToOneField(
        catalog.models.Order,
        django.db.models.CASCADE,
        verbose_name="заказ",
        help_text="заказ для оплаты",
        related_name="payment",
        related_query_name="payment",
    )
    payment_id = django.db.models.CharField(
        "идентификатор платежа",
        help_text="идентификатор платежа в платежной системе",
        max_length=255,
        blank=True,
        null=True,
    )
    status = django.db.models.CharField(
        "статус",
        help_text="статус платежа",
        max_length=9,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    created_at = django.db.models.DateTimeField(
        "дата создания",
        help_text="дата создания платежа",
    )
    confirmation_url = django.db.models.URLField(
        "url для подтверждения платежа",
        help_text="url для подтверждения платежа",
    )

    class Meta:
        verbose_name = "платёж"
        verbose_name_plural = "платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Платёж #{self.pk} / Заказ #{self.order.id}"

    def cancel(self):
        if self.status == PaymentStatus.PENDING:
            self.status = PaymentStatus.CANCELED
            self.save()
