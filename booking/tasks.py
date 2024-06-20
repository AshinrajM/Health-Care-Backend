from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task 
#@shared_task is a decorator that marks the task function as a Celery task.
def send_email(subject, message, to_email):
    print("check-----------------------------------------")
    print("check-----------------------------------------")
    print("check-----------------------------------------")
    print("check-----------------------------------------")
    from_email = settings.EMAIL_HOST_USER
    if isinstance(to_email, str):
        to_email = [to_email]
    send_mail(subject, message, from_email, to_email)
