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

@shared_task
def parse_resume_task(application_id):
    application = Application.objects.get(id=application_id)

    if not application.resume_snapshot:
        return "No resume found"

    print(f"Parsing resume: {application.resume_snapshot.name}")

    # Resume parsing logic will run here

    return "Resume parsing completed"

@shared_task
def trigger_ai_call_task(application_id):
    application = Application.objects.get(id=application_id)

    print(f"Triggering AI call for application: {application.id}")

    # AI call logic will run here

    return "AI call completed"

@shared_task
def periodic_test_task():
    print("Periodic Celery task is running!")
    return "Periodic task completed"
