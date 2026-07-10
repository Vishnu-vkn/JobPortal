from rest_framework import viewsets
from .models import Employer,Candidate
from .serializers import EmployerSerializer,CandidateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class EmployerViewSet(viewsets.ModelViewSet):
    queryset=Employer.objects.all()
    serializer_class=EmployerSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Employer.objects.filter(is_deleted="False")
        
        return Employer.objects.filter(user=self.request.user,is_deleted='False')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        instance.is_deleted=True
        instance.save()

        return Response(
            { "Message" : "Profile Deleted Successfully" },
            status=status.HTTP_200_OK
        )

    
class CandidateViewSet(viewsets.ModelViewSet):
    queryset=Candidate.objects.all()
    serializer_class=CandidateSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Candidate.objects.filter(is_deleted="False")
        
        return Candidate.objects.filter(user=self.request.user,is_deleted="False")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        instance.is_deleted=True
        instance.save()

        return Response(
            { "Message" : "Profile Deleted Successfully" },
            status=status.HTTP_200_OK
        )
    
