from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet,CandidateViewSet,ResumeUploadView,JobViewSet,PublicJobListView,LatestJobView,FeaturedJobView,ApplyJobView
from .views import LatestJobView,FeaturedJobView,ApplyJobView,MyApplicationView,MyApplicationDetailView


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
    path("applications/<int:pk>/",MyApplicationDetailView.as_view(),name="application-detail")
]

urlpatterns+=router.urls
