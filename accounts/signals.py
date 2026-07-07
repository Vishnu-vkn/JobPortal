from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

from jobportal.models import Employer,Candidate

@receiver(post_save,sender=CustomUser)
def create_profile(sender,instance,created,**kwargs):
    if created:
        if instance.role==CustomUser.Role.EMPLOYER:
            Employer.objects.create(user=instance)

        elif instance.role==CustomUser.Role.CANDIDATE:
            Candidate.objects.create(user=instance)