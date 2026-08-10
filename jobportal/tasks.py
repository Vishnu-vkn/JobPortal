from celery import shared_task
from .models import Application
from .services import(send_application_received_email,send_shortlisted_email,send_rejected_email)

#testtask
@shared_task
def test_task():
    print(" Celery task is working!")
    return "Task completed successfully"

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_application_received_email_task(application_id):
    application=Application.objects.get(id=application_id)
    send_application_received_email(application)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_shortlisted_email_task(application_id):
    application=Application.objects.get(id=application_id)
    send_shortlisted_email(application)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_rejected_email_task(application_id):
    application = Application.objects.get(id=application_id)
    send_rejected_email(application)
