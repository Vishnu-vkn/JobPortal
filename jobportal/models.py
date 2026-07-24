from django.db import models
from django.conf import settings

class Employer(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_deleted=models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    resume=models.FileField(upload_to="resumes/",blank=True,null=True)
    skills=models.TextField(blank=True)
    education=models.CharField(max_length=200,blank=True)
    experience=models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0
    )
    phone=models.CharField(max_length=15,blank=True)
    address=models.TextField(blank=True)
    is_deleted=models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
    
class JobType(models.TextChoices):
    #CONSTANT_NAME = "database_value", "display_name"(adminpanel/forms)
    FULL_TIME="Full Time","Full Time"
    PART_TIME="Part Time","Part Time"
    INTERNSHIP="Internship","Internship"
    CONTRACT="Contract","Contract"
    
class Job(models.Model):
    employer=models.ForeignKey(Employer,on_delete=models.CASCADE,related_name="jobs")
    title=models.CharField(max_length=100)
    description=models.TextField()
    skills=models.TextField(blank=True)
    experience=models.DecimalField(max_digits=4,decimal_places=1,default=0)
    salary=models.DecimalField(max_digits=10,decimal_places=2)
    location=models.CharField(max_length=100)
    job_type=models.CharField(max_length=20,choices=JobType.choices,default=JobType.FULL_TIME)
    status=models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    deadline=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    
class Application(models.Model):
        
    class Status(models.TextChoices):
        APPLIED="Applied","Applied"
        SHORTLISTED="Shortlisted","Shortlisted"
        INTERVIEW_SCHEDULED="Interview Scheduled","Interview Scheduled"
        REJECTED="Rejected","Rejected"
        SELECTED="Selected","Selected"

    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE,related_name="applications")
    job=models.ForeignKey(Job,on_delete=models.CASCADE,related_name="applications")
    applied_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.APPLIED)
    resume_snapshot=models.FileField(upload_to="application_resumes/",blank=True,null=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(
                fields=["candidate","job"],
                name="unique_candidate_job"
            )
        ]

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"


class ApplicationStatusLog(models.Model):
    application=models.ForeignKey(Application,on_delete=models.CASCADE,related_name="status_logs")
    previous_status=models.CharField(max_length=30,choices=Application.Status.choices)
    new_status=models.CharField(max_length=30,choices=Application.Status.choices)
    changed_by=models.ForeignKey(Employer,on_delete=models.CASCADE,related_name="status_updates")
    changed_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.application} | {self.previous_status} → {self.new_status} | {self.changed_by}"

class SavedJob(models.Model):

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="saved_jobs"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_saved_job"
            )
        ]

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"
    



