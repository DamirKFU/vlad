import django.db.models

import catalog.models


class OrderLogManager(django.db.models.Manager):
    def get_order_logs(self, order_id):
        return self.select_related("order", "user").filter(order_id=order_id)


class OrderLog(django.db.models.Model):
    objects = OrderLogManager()

    order = django.db.models.ForeignKey(
        catalog.models.Order,
        on_delete=django.db.models.CASCADE,
        related_name="logs",
        verbose_name="заказ",
    )
    from_status = django.db.models.CharField(
        "предыдущий статус",
        max_length=2,
        choices=catalog.models.OrderStatus.choices,
    )
    to_status = django.db.models.CharField(
        "новый статус",
        max_length=2,
        choices=catalog.models.OrderStatus.choices,
    )
    user = django.db.models.ForeignKey(
        "users.User",
        on_delete=django.db.models.SET_NULL,
        null=True,
        verbose_name="пользователь",
    )
    created_at = django.db.models.DateTimeField(
        "дата создания",
        auto_now_add=True,
    )
    error_comment = django.db.models.TextField(
        "комментарий об ошибке",
        blank=True,
        null=True,
        help_text="заполняется только при возврате на предыдущий статус",
    )

    class Meta:
        verbose_name = "лог заказа"
        verbose_name_plural = "логи заказов"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Заказ #{self.order.id}: {self.from_status} -> {self.to_status}"
        )
