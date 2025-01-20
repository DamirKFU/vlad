import catalog.models
import staff.logs
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

    if users.models.Role.DEVELOPER in user_roles:
        return [
            catalog.models.OrderStatus.PAID,
            catalog.models.OrderStatus.IN_WORK,
            catalog.models.OrderStatus.DRAFT,
            catalog.models.OrderStatus.IN_DELIVERY,
            catalog.models.OrderStatus.DELIVERED,
            catalog.models.OrderStatus.CANCELED,
        ]

    allowed_statuses = []
    if users.models.Role.DESIGNER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.PAID)

    if users.models.Role.EMBROIDERER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.IN_WORK)

    if users.models.Role.CURIER in user_roles:
        allowed_statuses.append(catalog.models.OrderStatus.DRAFT)

    return allowed_statuses


def get_allowed_chats(user):
    if user.is_superuser:
        return ["my", "unassigned", "assigned"]

    return ["my", "unassigned"]


def handle_status_change(order, new_status, user, error_comment=None):
    old_status = order.status
    order.status = new_status
    order.save()

    staff.logs.log_order_status_change(
        order,
        user,
        old_status,
        new_status,
        error_comment=error_comment,
    )
