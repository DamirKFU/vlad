import django.db.models.signals
import django.dispatch

import catalog.models
import telegram_bot
import telegram_bot.bot


@django.dispatch.receiver(
    django.db.models.signals.pre_save, sender=catalog.models.Order
)
def notify_status_change(sender, instance, **kwargs):
    old_instance = catalog.models.Order.objects.get_for_telegram_bot(
        instance.pk
    )
    if old_instance is None:
        return

    return

    if (
        old_instance.status != instance.status
        and old_instance.user.telegram_id
    ):
        telegram_bot.bot.send_order_status_update(
            old_instance.user.telegram_id,
            instance.id,
            instance.status,
        )
