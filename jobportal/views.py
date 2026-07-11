from rest_framework import viewsets
from .models import Employer,Candidate
from .serializers import EmployerSerializer,CandidateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os
from rest_framework.views import APIView 

class EmployerViewSet(viewsets.ModelViewSet):
    queryset=Employer.objects.all()
    serializer_class=EmployerSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Employer.objects.filter(is_deleted=False)
        
        return Employer.objects.filter(user=self.request.user,is_deleted=False)

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
            return Candidate.objects.filter(is_deleted=False)
        
        return Candidate.objects.filter(user=self.request.user,is_deleted=False)

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
    
class ResumeUploadView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        candidate=Candidate.objects.get(user=request.user)
        resume=request.FILES.get("resume")

        if not resume:
            return Response(
                {"error":"No resume uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        allowed_extensions=[".pdf",".docx",".doc"]
        extension=os.path.splitext(resume.name)[1].lower()

        if extension not in allowed_extensions:
            return Response(
                {
                    "error":"Only PDF, DOC and DOCX Files are allowed"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        max_size=5*1024*1024  #5MB
        if resume.size>max_size:
            return Response(
                {"error":"File size should not exceed 5MB"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if candidate.resume:
            candidate.resume.delete(save=False)

        candidate.resume=resume
        candidate.save()

        return Response(
            {"message":"Resume Uploaded Successfully"},
            status=status.HTTP_200_OK
        )
    
