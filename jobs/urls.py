from django.urls import path
from .views import JobListAPIView
from .views import JobCreateAPIView

urlpatterns = [
    path("jobs/",JobListAPIView.as_view()),
    path("jobs/create/", JobCreateAPIView.as_view()),

]