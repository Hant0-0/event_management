from celery import shared_task
from django.core.mail import send_mail

from core.settings import EMAIL_HOST_USER


@shared_task
def message_for_register_event(email, full_name, date_event):
    send_mail(
        "Invitation to Join Our Event",
        f"Hello, {full_name}!\n\nWe are pleased to invite you to join our upcoming event, which will take place on {date_event}."
        f"\n\nThis is a great "
        "opportunity for idea exchange and collaboration. Don’t miss the chance to be a part of this event!\n\nWe look forward to your presence!",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )