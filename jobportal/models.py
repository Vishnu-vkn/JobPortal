from django.db import models

class User(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=255)
    role=models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Employer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    company_name=models.CharField(max_length=100)
    website=models.URLField()
    location=models.CharField(max_length=100)

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    resume=models.FileField(upload_to="resumes/")
    skills=models.TextField()
    education=models.CharField(max_length=200)
    experience=models.PositiveBigIntegerField(default=0)
    phone=models.CharField(max_length=15)
    address=models.TextField()

    def __str__(self):
        return self.user.name
    
    
class Job(models.Model):
    employer=models.ForeignKey(Employer,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    description=models.TextField()
    salary=models.DecimalField(max_digits=10,decimal_places=2)
    location=models.CharField(max_length=100)
    deadline=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE)
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    applied_at=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,default="Applied")

    def __str__(self):
        return f"{self.candidate.user.name} - {self.job.title}"


