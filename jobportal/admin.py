from django.contrib import admin
from .models import  Employer, Candidate, Job, Application,ApplicationStatusLog


admin.site.register(Job)
admin.site.register(Application)

@admin.register(ApplicationStatusLog)
class ApplicationStatusLogAdmin(admin.ModelAdmin):
    readonly_fields = (
        "application",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



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