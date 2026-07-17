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
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE)
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    applied_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,default="Applied")

    def __str__(self):
        return f"{self.candidate.user.username} - {self.job.title}"


