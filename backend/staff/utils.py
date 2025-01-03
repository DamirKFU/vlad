import catalog.models
import staff.models
import users.models


def get_allowed_statuses(user):
    if user.is_superuser:
        return [
            catalog.models.OrderStatus.PAID,
            catalog.models.OrderStatus.IN_WORK,
            catalog.models.OrderStatus.DRAFT,
            catalog.models.OrderStatus.IN_DELIVERY,
            catalog.models.OrderStatus.DELIVERED,
            catalog.models.OrderStatus.CANCELED,
        ]

    user_roles = set(user.roles.values_list("role", flat=True))

    if users.models.Role.MODERATOR in user_roles:
        return [
            catalog.models.OrderStatus.PAID,
            catalog.models.OrderStatus.IN_WORK,
            catalog.models.OrderStatus.DRAFT,
        ]

    allowed_statuses = []
    if users.models.Role.DESIGNER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.PAID)

    if users.models.Role.EMBROIDERER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.IN_WORK)

    if users.models.Role.CURIER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.DRAFT)

    return allowed_statuses


def handle_status_change(
    order, new_status, user, is_return=False, error_comment=None
):
    old_status = order.status
    order.status = new_status
    order.save()

    staff.models.OrderLog.objects.create(
        order=order,
        from_status=old_status,
        to_status=new_status,
        user=user,
        error_comment=error_comment if is_return else None,
    )
