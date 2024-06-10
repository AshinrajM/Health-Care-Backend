from django.core.mail import send_mail
from django.conf import settings


def send_notification_email(subject, message, to_email):
    print("check", subject, message, to_email)
    from_email = settings.EMAIL_HOST_USER
    if isinstance(to_email, str):
        to_email = [to_email]
    send_mail(subject, message, from_email, to_email)
  