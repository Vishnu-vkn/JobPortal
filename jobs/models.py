from django.db import models

class User(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()

    def __str__(self):
        return self.name
    
class Job(models.Model):
    title=models.CharField(max_length=100)
    company=models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    job=models.ForeignKey(Job,on_delete=models.CASCADE)
    applied_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.job}"
