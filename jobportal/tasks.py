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

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def trigger_ai_call_task(self, application_id):
    from django.utils import timezone

    application = Application.objects.get(id=application_id)

    # Task has started
    application.ai_call_status = Application.AICallStatus.IN_PROGRESS
    application.ai_call_started_at = timezone.now()

    application.save(
        update_fields=[
            "ai_call_status",
            "ai_call_started_at",
        ]
    )

    print(f"Triggering AI call for application: {application.id}")

    try:
        # AI call logic will run here
        # Temporary failure test

        application.ai_call_status = Application.AICallStatus.COMPLETED
        application.ai_call_completed_at = timezone.now()

        application.save(
            update_fields=[
                "ai_call_status",
                "ai_call_completed_at",
            ]
        )

        return "AI call completed"

    except Exception:
        retry_count = self.request.retries + 1

        application.ai_call_retry_count = min(
            retry_count,
            self.max_retries
        )

        if self.request.retries >= self.max_retries:
            # Final attempt failed
            application.ai_call_status = Application.AICallStatus.FAILED
            application.ai_call_failed_at = timezone.now()

            application.save(
                update_fields=[
                    "ai_call_status",
                    "ai_call_failed_at",
                    "ai_call_retry_count",
                ]
            )
        else:
            # Celery will retry
            application.ai_call_status = Application.AICallStatus.QUEUED

            application.save(
                update_fields=[
                    "ai_call_status",
                    "ai_call_retry_count",
                ]
            )

        raise