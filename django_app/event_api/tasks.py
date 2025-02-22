from celery import shared_task
from django.core.mail import send_mail


@shared_task
def message_for_register_event(email):
    send_mail(
        "Subject here",
        "Here is the message.",
        "manoylo.maksimka@example.com",
        [email],
        fail_silently=False,
    )