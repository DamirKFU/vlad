import django.core.management.base

import users.documents
import users.models


class Command(django.core.management.base.BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("Начало переиндексации..."))
        users_objects = users.models.User.objects.all()
        users.documents.UserDocument().update(users_objects)
        self.stdout.write(self.style.SUCCESS("Переиндексация завершена"))
