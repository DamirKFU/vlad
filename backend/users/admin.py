import django.contrib

import users.models


@django.contrib.admin.register(users.models.User)
class UserAdmin(django.contrib.admin.ModelAdmin):
    fields = (
        users.models.User.username.field.name,
        users.models.User.email.field.name,
        users.models.User.roles.field.name,
        users.models.User.telegram_id.field.name,
    )
    readonly_fields = (
        users.models.User.username.field.name,
        users.models.User.email.field.name,
    )
    filter_horizontal = (users.models.User.roles.field.name,)


@django.contrib.admin.register(users.models.UserRole)
class UserRoleAdmin(django.contrib.admin.ModelAdmin):
    pass
