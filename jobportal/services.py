#ATS Logic
from decimal import Decimal
from .models import Application,ApplicationStatusLog,Notification,EmailLog
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

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

