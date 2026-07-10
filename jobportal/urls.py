from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet,CandidateViewSet

router=DefaultRouter()

router.register("employers",EmployerViewSet)
router.register("candidates",CandidateViewSet)

urlpatterns=router.urls