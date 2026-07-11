from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet,CandidateViewSet,ResumeUploadView

router=DefaultRouter()

router.register("employers",EmployerViewSet)
router.register("candidates",CandidateViewSet)


urlpatterns=[
    path("candidates/uploadresume/",ResumeUploadView.as_view(),name="uploadresume")
]

urlpatterns+=router.urls
