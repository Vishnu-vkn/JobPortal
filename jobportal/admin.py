from django.contrib import admin
from .models import  Employer, Candidate, Job, Application


admin.site.register(Job)
admin.site.register(Application)



@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "education",
        "experience",
        "is_deleted",
    )

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_name",
        "location",
        "is_deleted",
    )