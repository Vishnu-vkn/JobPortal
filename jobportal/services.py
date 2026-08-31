#ATS Logic
from decimal import Decimal
from .models import Application,ApplicationStatusLog,Notification,EmailLog,AIInterviewSession,CallLog
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import time,datetime,timedelta
from django.utils import timezone


CALL_START_TIME = time(9, 0)    # 09:00 AM
CALL_END_TIME = time(18, 0)     # 06:00 PM

def calculate_ats_score(job,candidate):
    #calculate ats score between a job and a candidate
    #convert comma seperated skills into python lists 
    job_skills=[
        skill.strip().lower()
        for skill in job.skills.split(",")
        if skill.strip()
    ]

    candidate_skills=[
        skill.strip().lower()
        for skill in candidate.skills.split(",")
        if skill.strip()
    ]

    #find matchedskills
    matched_skills=[]
    for skill in job_skills:
        if skill in candidate_skills:
            matched_skills.append(skill)

    #skills score(70 marks)
    if job_skills:
        skills_score=(len(matched_skills)/len(job_skills))*70
    else:
        skills_score=0

    #Experience score(20marks)
    if candidate.experience>=job.experience:
        experience_score=20
    elif job.experience>0:
        experience_score=(float(candidate.experience)/float(job.experience))*20 
        
    else:
        experience_score=20

    #Education Score
    if(
        candidate.education and candidate.education.lower()=="bachelor"
    ):
        education_score=10
    else:
        education_score=5

    total_score=round(skills_score+experience_score+education_score,2)


    return{
        "score":total_score,
        "matched_skills":matched_skills
    }


def check_eligibility(application):

    previous_status=application.status

    if application.ats_score>=application.job.minimum_score:
        new_status=Application.Status.SHORTLISTED
    else:
        new_status=Application.Status.REJECTED

    application.status=new_status
    application.save(update_fields=["status"])

    ApplicationStatusLog.objects.create(
        application=application,
        previous_status=previous_status,
        new_status=new_status,
        changed_by=None
    )

    if new_status == Application.Status.SHORTLISTED:
        send_notification(
            candidate=application.candidate,
            application=application,
            title="Application Shortlisted",
            message=f"Congratulations! You have been shortlisted for {application.job.title}."
        )

        from .tasks import send_shortlisted_email_task
        send_shortlisted_email_task.delay(application.id)

    else:
        send_notification(
            candidate=application.candidate,
            application=application,
            title="Application Rejected",
            message=f"Unfortunately, your application for {application.job.title} was not shortlisted."
        )

        from .tasks import send_rejected_email_task
        send_rejected_email_task.delay(application.id)

def send_notification(candidate, application, title, message):
    Notification.objects.create(
        candidate=candidate,
        application=application,
        title=title,
        message=message
    )


#day27email
def send_application_received_email(application):
    candidate = application.candidate
    job = application.job

    html_message = render_to_string(
    "emails/application_received.html",
    {
        "candidate_name": candidate.user.first_name,
        "job_title": job.title,
    }
    )  

    try:
        send_mail(
            subject="Application Received",
            message=(
                f"Hi {candidate.user.first_name},\n\n"
                f"We have successfully received your application for "
                f" {job.title}."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        EmailLog.objects.create(
            recipient=candidate.user.email,
            subject="Application Received",
            status=EmailLog.Status.SUCCESS
        )

    except Exception as e:
        EmailLog.objects.create(
            recipient=candidate.user.email,
            subject="Application Received",
            status=EmailLog.Status.FAILED,
            error_message=str(e),
        )

        raise

def send_shortlisted_email(application):
    candidate = application.candidate
    job = application.job

    html_message = render_to_string(
        "emails/shortlisted.html",
        {
            "candidate_name": candidate.user.first_name,
            "job_title": job.title,
        },
    )

    try:
        send_mail(
            subject="Application Shortlisted",
            message=(
                f"Congratulations {candidate.user.first_name},\n\n"
                f"Your application for {job.title} has been shortlisted."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        EmailLog.objects.create(
                    recipient=candidate.user.email,
                    subject="Application Shortlisted",
                    status=EmailLog.Status.SUCCESS
        )
    except Exception as e:
        EmailLog.objects.create(
                    recipient=candidate.user.email,
                    subject="Application Shortlisted",
                    status=EmailLog.Status.FAILED,
                    error_message=str(e),
                )
        raise
        

def send_rejected_email(application):

    candidate = application.candidate
    job = application.job

    html_message = render_to_string(
        "emails/rejected.html",
        {
            "candidate_name": candidate.user.first_name,
            "job_title": job.title,
        },
    )

    try:

        send_mail(
            subject="Application Rejected",
            message=(
                f"Hello {candidate.user.first_name},\n\n"
                f"Thank you for applying for {job.title}."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        EmailLog.objects.create(
                            recipient=candidate.user.email,
                            subject="Application Rejected",
                            status=EmailLog.Status.SUCCESS
                )

    except Exception as e:
        EmailLog.objects.create(
                            recipient=candidate.user.email,
                            subject="Application Rejected",
                            status=EmailLog.Status.FAILED,
                            error_message=str(e),
                        )
        raise

#day33
def is_ats_eligible(application):
    return application.ats_score >= application.job.minimum_score

def is_job_active(application):
    return application.job.status

def is_candidate_available(application):
    return application.candidate.is_available

def check_application_eligibility(application):
    if not is_ats_eligible(application):
        return False, "ATS score is below the required threshold."

    if not is_job_active(application):
        return False, "Job is not active."

    if not is_candidate_available(application):
        return False, "Candidate is not available."

    return True, "Application is eligible."

def trigger_ai_call(application,triggered_by=None):

    eligible, reason = check_application_eligibility(application)

    if not eligible:
        return {
            "triggered": False,
            "reason": reason
        }

    if not is_within_calling_window():
        return {
            "triggered": False,
            "reason": "Current time is outside the AI calling window."
        }
        
    session = AIInterviewSession.objects.create(
    application=application)
        
    reason="Application is eligible for AI Call"
    CallLog.objects.create(
        session=session,
        triggered_by=triggered_by,
        reason=reason
    )
    
    return {
    "triggered": True,
    "reason": reason }
    
def is_within_calling_window(current_time=None):
    if current_time is None:
        current_time = timezone.localtime().time()

    return CALL_START_TIME <= current_time < CALL_END_TIME

def get_next_call_time(current_datetime=None):

    if current_datetime is None:
        current_datetime = timezone.localtime()

    current_time = current_datetime.time()

    if CALL_START_TIME <= current_time < CALL_END_TIME:
        return current_datetime

    if current_time < CALL_START_TIME:
        return current_datetime.replace(
            hour=CALL_START_TIME.hour,
            minute=CALL_START_TIME.minute,
            second=0,
            microsecond=0
        )

    next_day = current_datetime + timedelta(days=1)

    return next_day.replace(
        hour=CALL_START_TIME.hour,
        minute=CALL_START_TIME.minute,
        second=0,
        microsecond=0
    )
    
def schedule_ai_call(application):
    eligible, reason = check_application_eligibility(application)

    if not eligible:
        return {
            "scheduled": False,
            "reason": reason
        }

    scheduled_time = get_next_call_time()

    from django.utils import timezone
    from .tasks import trigger_ai_call_task

    trigger_ai_call_task.apply_async(
        args=[application.id],
        eta=scheduled_time
    )

    # Mark call as queued
    application.ai_call_status = Application.AICallStatus.QUEUED
    application.ai_call_queued_at = timezone.now()
    application.save(
        update_fields=[
            "ai_call_status",
            "ai_call_queued_at"
        ]
    )

    return {
        "scheduled": True,
        "scheduled_time": scheduled_time,
        "reason": "AI call scheduled successfully."
    }
    
def save_transcript(session, conversation):

    session.transcript = {
        "conversation": conversation
    }

    session.save(update_fields=["transcript", "updated_at"])

    return session