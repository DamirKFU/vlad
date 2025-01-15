import django.conf
import django.core.management.base

import users.models


class Command(django.core.management.base.BaseCommand):

    def handle(self, *args, **options):
        if users.models.User.objects.count() == 0:
            for user in django.conf.settings.ADMINS:
                username = user[0].replace(" ", "")
                email = user[1]
                password = "admin"
                self.stdout.write(
                    self.style.HTTP_INFO(
                        "Creating account for %s (%s)" % (username, email)
                    )
                )
                admin = users.models.User.objects.create_superuser(
                    email=email, username=username, password=password
                )
                admin.is_active = True
                admin.is_admin = True
                admin.save()
        else:
            self.stdout.write(
                self.style.HTTP_INFO(
                    "Admin accounts can only be initialized if "
                    "no accounts exist"
                )
            )
