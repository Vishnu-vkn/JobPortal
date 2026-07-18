from rest_framework import viewsets
from .models import Employer,Candidate , Job,Application
from .serializers import EmployerSerializer,CandidateSerializer,JobSerializer,ApplicationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView 
import os
from rest_framework.views import APIView 
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsEmployer ,IsCandidate
from django.db.models import Q
from firstproject.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

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
    
#API for All Active Jobs
class PublicJobListView(ListAPIView):
    serializer_class=JobSerializer
    permission_classes=[AllowAny]
    pagination_class=CustomPagination

    def get_queryset(self):
        queryset=queryset = Job.objects.filter(status=True)
    
        #filtering
        location=self.request.query_params.get("location")
        job_type=self.request.query_params.get("job_type")
        skill=self.request.query_params.get("skill")
        salary_min=self.request.query_params.get("salary_min")
        salary_max=self.request.query_params.get("salary_max")
        experience_min=self.request.query_params.get("experience_min")
        experience_max=self.request.query_params.get("experience_max")

        if location:
            queryset=queryset.filter(location__icontains=location)
        if job_type:
            queryset=queryset.filter(job_type=job_type)
        if skill:
            queryset=queryset.filter(skills__icontains=skill)
        if salary_min:
            queryset=queryset.filter(salary__gte=salary_min)
        if salary_max:
            queryset=queryset.filter(salary__lte=salary_max)

        if experience_min:
            queryset=queryset.filter(experience__gte=experience_min)
        if experience_max:
            queryset=queryset.filter(experience__lte=experience_max)

        #searching
        search=self.request.query_params.get("search")

        if search:
            queryset=queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(skills__icontains=search) |
                Q(location__icontains=search)
            )



        return queryset


#API for Latest Jobs
class LatestJobView(ListAPIView):
    serializer_class=JobSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        return Job.objects.filter(status=True).order_by("-created_at") #minus symbol at front (descending order)-newest jobs first
    
#API for Featured Jobs
class FeaturedJobView(ListAPIView):
    serializer_class=JobSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        return Job.objects.filter(
            status=True,
            is_featured=True
        )    
    

#API for Applying Job
class ApplyJobView(APIView):
    permission_classes=[IsAuthenticated , IsCandidate]

    def post(self,request,job_id):
        job=get_object_or_404(Job,id=job_id)  #step 1 get the job
        candidate=request.user.candidate  #step 2 get candidate
        if not candidate.resume:   #step 3  check resume
            return Response(
                {
                    "error":"Please Upload your resume before applying"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not job.status:  #step 4 check job status
            return Response(
                {
                    "error":"This job is no longer accepting applications"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Application.objects.filter(   #step 5 duplicate check
            candidate=candidate,
            job=job
        ).exists():
            return Response(
                {
                    "error":"You have already applied for this job "
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        #step 6 create application
        application=Application.objects.create(
            candidate=candidate,
            job=job,
            resume_snapshot=candidate.resume
        )

        #step 7 serialize response
        serializer=ApplicationSerializer(application)
        return Response(
            {
                "message":"Job Applied Successfully",
                "data":serializer.data
            },
            status=status.HTTP_201_CREATED
        )

        
class MyApplicationView(ListAPIView):
    permission_classes=[IsAuthenticated,IsCandidate]
    serializer_class=ApplicationSerializer
    
    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user.candidate
        ).select_related("job")


    
class MyApplicationDetailView(RetrieveAPIView):  #retrieveapiview return one object
    serializer_class=ApplicationSerializer
    permission_classes=[IsAuthenticated,IsCandidate]

    def get_object(self):
        return get_object_or_404(
            Application,
            id=self.kwargs["pk"],
            candidate=self.request.user.candidate
        )