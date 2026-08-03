from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet,CandidateViewSet,ResumeUploadView,JobViewSet,PublicJobListView,LatestJobView,FeaturedJobView,ApplyJobView
from .views import LatestJobView,FeaturedJobView,ApplyJobView,MyApplicationView,MyApplicationDetailView,ApplicationStatusUpdateView
from .views import EmployerJobListView,EmployerJobUpdateView,EmployerCloseJobView,EmployerApplicationListView
from .views import EmployerDashboardAPI,CandidateDashboardAPI , ApplicationTimelineView , SaveJobView,UnsaveJobView , SavedJobListView
from .views import RecommendedJobListView , ApproveEmployerView, BlockUserView,AdminJobListView,AdminJobDeleteView,AdminDashboardView
from .views import UserGrowthView,JobActivityView,FlagJobView,AuditLogListView

router=DefaultRouter()

router.register("employers",EmployerViewSet)
router.register("candidates",CandidateViewSet)
router.register("jobs",JobViewSet)


urlpatterns=[
    path("candidates/uploadresume/",ResumeUploadView.as_view(),name="uploadresume"),
    path("jobs/public/",PublicJobListView.as_view(),name="public-jobs"),
    path("jobs/latest/",LatestJobView.as_view(),name="latest-jobs"),
    path("jobs/featured/",FeaturedJobView.as_view(),name="featured-jobs"),
    path("jobs/<int:job_id>/apply/",ApplyJobView.as_view(),name="apply-job"),
    path("applications/",MyApplicationView.as_view(),name="my-applications"),
    path("applications/<int:pk>/",MyApplicationDetailView.as_view(),name="application-detail"),
    path("applications/<int:pk>/status/",ApplicationStatusUpdateView.as_view(),name="application-status-update"),
    path("employer/jobs/",EmployerJobListView.as_view(),name="employer_job_list"),
    path("employer/jobs/<int:pk>/",EmployerJobUpdateView.as_view(),name="employer_job_update"),
    path("employer/jobs/<int:pk>/close/",EmployerCloseJobView.as_view(),name="employer_job_close"),
    path("employer/jobs/<int:pk>/applications/",EmployerApplicationListView.as_view(),name="employer_application_list"),
    path("employer/dashboard/",EmployerDashboardAPI.as_view(),name="employer_dashboard"),
    path("candidate/dashboard/",CandidateDashboardAPI.as_view(),name="candidate_dashboard"),
    path("candidate/applications/<int:pk>/timeline/",ApplicationTimelineView.as_view(),name="application-timeline",),
    path("candidate/jobs/<int:pk>/save/",SaveJobView.as_view(),name="save-job",),
    path("candidate/jobs/<int:pk>/unsave/",UnsaveJobView.as_view(),name="unsave-job",),
    path("candidate/savedjobs/",SavedJobListView.as_view(),name="saved-job-list"),
    path("candidate/recommendedjobs/",RecommendedJobListView.as_view(),name="recommendedjobs"),
    path("admin/employers/<int:pk>/approve/",ApproveEmployerView.as_view(), name="approve-employer",),
    path("admin/users/<int:pk>/block/",BlockUserView.as_view(),name="block-user",),
    path("admin/jobs/", AdminJobListView.as_view(),name="admin-job-list",),
    path("admin/jobs/<int:pk>/",AdminJobDeleteView.as_view(),name="admin-job-delete",),
    path("admin/dashboard/",AdminDashboardView.as_view(),name="admin-dashboard",),
    path("admin/usergrowth/",UserGrowthView.as_view(),name="user-growth",),
    path("admin/jobactivity/",JobActivityView.as_view(),name="job-activity",),
    path("admin/jobs/<int:pk>/flag/",FlagJobView.as_view(),name="flag-job",),
    path("admin/auditlogs/",AuditLogListView.as_view(),name="audit-logs",)
]

urlpatterns+=router.urls
