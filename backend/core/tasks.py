import celery
import celery.states
import django.conf
import django.core.mail


@celery.shared_task(bind=True)
def send_email_task(self, **data):
    return django.core.mail.send_mail(**data)
