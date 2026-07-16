from rest_framework import viewsets
from .models import Employer,Candidate , Job
from .serializers import EmployerSerializer,CandidateSerializer,JobSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os
from rest_framework.views import APIView 
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsEmployer

#Code Refactoring
class SoftDeleteMixin:
    def destroy(self,request,*args,**kwargs):
        instance=self.get_object()
        instance.is_deleted=True
        instance.save()

        return Response(
            {"message":"Profile Deleted Successfully"},
            status=status.HTTP_200_OK
        )

class EmployerViewSet(SoftDeleteMixin,viewsets.ModelViewSet):
    queryset=Employer.objects.select_related("user")
    serializer_class=EmployerSerializer
    permission_classes=[IsAuthenticated]
    filter_backends=[DjangoFilterBackend,SearchFilter]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Employer.objects.filter(is_deleted=False)
        
        return Employer.objects.filter(user=self.request.user,is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
class CandidateViewSet(SoftDeleteMixin,viewsets.ModelViewSet):
    queryset=Candidate.objects.select_related("user")
    serializer_class=CandidateSerializer
    permission_classes=[IsAuthenticated]
    
    filter_backends=[DjangoFilterBackend,SearchFilter]
    filterset_fields={
        "experience":["exact","gte","lte","gt","lt"],
        "is_deleted":["exact"]
    }

    search_fields=["skills","education","phone","address","user__username","user__email"]


    def get_queryset(self):
        if self.request.user.is_staff:
            return Candidate.objects.filter(is_deleted=False)
        
        return Candidate.objects.filter(user=self.request.user,is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
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
    
class JobViewSet(viewsets.ModelViewSet):
    queryset=Job.objects.all()
    serializer_class=JobSerializer
    permission_classes=[IsAuthenticated,IsEmployer]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user.employer)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Job.objects.all()
        
        return Job.objects.filter(employer=self.request.user.employer)

