from celery import shared_task
from django.core.mail import send_mail


@shared_task 
#@shared_task is a decorator that marks the my_task function as a Celery task.
def send_email(subject, message, to_email):
    print("check", subject, message, to_email)
    from_email = settings.EMAIL_HOST_USER
    if isinstance(to_email, str):
        to_email = [to_email]
    send_mail(subject, message, from_email, to_email)
