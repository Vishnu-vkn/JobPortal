from rest_framework import viewsets
from rest_framework import generics
from .models import Employer,Candidate , Job,Application,ApplicationStatusLog,SavedJob,AuditLog
from .serializers import EmployerSerializer,CandidateSerializer,JobSerializer,ApplicationSerializer,ApplicationStatusSerializer,RecentApplicationSerializer
from .serializers import ApplicationStatusLogSerializer ,  SavedJobSerializer,AuditLogSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny ,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView , UpdateAPIView
import os
from rest_framework.views import APIView 
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsEmployer ,IsCandidate
from django.db.models import Q
from firstproject.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta


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
        employer=self.request.user.employer

        if not employer.is_approved:
            raise PermissionDenied("Your account is waiting approval")

        serializer.save(employer=employer)

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
    
class ApplicationStatusUpdateView(UpdateAPIView):
    queryset=Application.objects.all()
    serializer_class=ApplicationStatusSerializer
    permission_classes=[IsAuthenticated]
    lookup_field="pk"

    def get_object(self):
        application=get_object_or_404(
            Application,
            pk=self.kwargs["pk"],
            job__employer=self.request.user.employer

        )
        return application
    
    def update(self,request,*args,**kwargs):
        application=self.get_object()
        current_status=application.status
        allowed_transitions = {
        Application.Status.APPLIED: [
            Application.Status.SHORTLISTED,
            Application.Status.REJECTED,
         ],

        Application.Status.SHORTLISTED: [
            Application.Status.INTERVIEW_SCHEDULED,
            Application.Status.REJECTED,
        ],

        Application.Status.INTERVIEW_SCHEDULED: [
            Application.Status.SELECTED,
            Application.Status.REJECTED,
        ],

        Application.Status.REJECTED: [],

        Application.Status.SELECTED: [],
        }

        new_status=request.data.get("status")

        if new_status not in allowed_transitions[current_status]:
            return Response(
                {
                    
                 "detail": f"Cannot change status from '{current_status}' to '{new_status}'."

                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response= super().update(request,*args,**kwargs)

        ApplicationStatusLog.objects.create(
            application=application,
            previous_status=current_status,
            new_status=new_status,
            changed_by=request.user.employer
        )

        return response
    
#This API manages the jobs posted by the employer.
class EmployerJobListView(ListAPIView):
    serializer_class=JobSerializer
    permission_classes=[IsAuthenticated,IsEmployer]
    pagination_class=CustomPagination

    def get_queryset(self):
        employer=self.request.user.employer
        return Job.objects.filter(employer=employer).select_related("employer").order_by("-created_at")
    
#This API Employer Job Update API.
class EmployerJobUpdateView(UpdateAPIView):
    serializer_class=JobSerializer
    permission_classes=[IsAuthenticated,IsEmployer]

    def get_queryset(self):
        employer=self.request.user.employer
        return Job.objects.filter(employer=employer).select_related("employer")

#This API used for closing an job
class EmployerCloseJobView(UpdateAPIView):
    serializer_class=JobSerializer
    permission_classes=[IsAuthenticated,IsEmployer]

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user.employer)
    
    def patch(self,request,*args,**kwargs):
        job=self.get_object()
        job.status=False
        job.save()

        return Response(
            {
                "message":"Job Closed Successfully"
            },
            status=status.HTTP_200_OK
        )
    
class EmployerApplicationListView(ListAPIView):
    serializer_class=ApplicationSerializer
    permission_classes=[IsAuthenticated,IsEmployer]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["status"]
    search_fields = [
        "candidate__user__first_name",
        "candidate__user__last_name",
        "candidate__user__email",
    ]

    def get_queryset(self):
        job=get_object_or_404(Job,pk=self.kwargs["pk"],employer=self.request.user.employer)

        return(
            Application.objects.filter(job=job)
            .select_related("candidate","job","candidate__user")
            .order_by("-applied_at")
        )


#APIView is the best choice because we're computing statistics rather than retrieving a single model.
#API for Employer Dashboard Analytics
class EmployerDashboardAPI(APIView):
    permission_classes=[IsAuthenticated,IsEmployer]

    def get(self,request):
        employer=request.user.employer

        jobs=Job.objects.filter(employer=employer)

        total_jobs=jobs.count()
        active_jobs=jobs.filter(status=True).count()
        closed_jobs=jobs.filter(status=False).count()

        applications=Application.objects.filter(job__employer=employer)

        total_applications=applications.count()

        shortlisted=applications.filter(
            status=Application.Status.SHORTLISTED
        ).count()

        shortlist_ratio=(
            round((shortlisted/total_applications)*100,2)
            if total_applications>0
            else 0
        )

        return Response({
            "total_jobs":total_jobs,
            "active_jobs":active_jobs,
            "closed_jobs":closed_jobs,
            "total_applications":total_applications,
            "shortlisted":shortlisted,
            "shortlist_ratio":f"{shortlist_ratio}%"        
        })


#API for Candidate Dashboard API
class CandidateDashboardAPI(APIView):
    permission_classes=[IsAuthenticated,IsCandidate]

    def get(self,request):
        candidate=request.user.candidate
        applications=Application.objects.filter(candidate=candidate)
        total_applications=applications.count()

        applied = applications.filter(
        status=Application.Status.APPLIED
        ).count()

        shortlisted = applications.filter(
        status=Application.Status.SHORTLISTED
        ).count()

        interview_scheduled = applications.filter(
        status=Application.Status.INTERVIEW_SCHEDULED
        ).count()

        selected = applications.filter(
        status=Application.Status.SELECTED
        ).count()

        rejected = applications.filter(
        status=Application.Status.REJECTED
        ).count()

        recent_applications=(
            applications.select_related("job").order_by("-applied_at")[:5]
        )

        serializer = RecentApplicationSerializer(recent_applications,many=True)

        return Response({
            "total_applications":total_applications,
            "applied":applied,
            "shortlisted":shortlisted,
            "interview_scheduled":interview_scheduled,
            "selected":selected,
            "rejected":rejected,
            "recent_applications":serializer.data
        })

class ApplicationTimelineView(APIView):
    permission_classes=[IsAuthenticated,IsCandidate]

    def get(self,request,pk):
        candidate=request.user.candidate
        application=get_object_or_404(
            Application,
            id=pk,
            candidate=candidate
        )

        timeline=(
            application.status_logs.all()
        )

        serializer=ApplicationStatusLogSerializer(timeline,many=True)
        return Response({
            "current_status": application.status,
            "timeline":serializer.data
            })


class SaveJobView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request, pk):
        candidate = request.user.candidate

        job = get_object_or_404(Job, id=pk)

        saved_job, created = SavedJob.objects.get_or_create(  #get_or_create() first checks whether the record already exists:
            candidate=candidate,
            job=job
        )

        if created:
            return Response(
                {"message": "Job saved successfully."},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"message": "Job already saved."},
            status=status.HTTP_200_OK
        )

class UnsaveJobView(APIView):
    permission_classes = [IsAuthenticated, IsCandidate]

    def delete(self, request, pk):

        candidate = request.user.candidate

        saved_job = get_object_or_404(
            SavedJob,
            candidate=candidate,
            job_id=pk
        )

        saved_job.delete()

        return Response(
            {"message": "Job removed from saved jobs."},
            status=status.HTTP_200_OK
        )

class SavedJobListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsCandidate]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        candidate = self.request.user.candidate

        return SavedJob.objects.filter(
            candidate=candidate
        ).select_related("job")
        
#API for Profile-based Recommendations
class RecommendedJobListView(ListAPIView):
    permission_classes=[IsAuthenticated,IsCandidate]
    serializer_class=JobSerializer

    def get_queryset(self):
        candidate=self.request.user.candidate
        candidate_skills=candidate.skills
        candidate_experience=candidate.experience

        return Job.objects.filter(
            status=True,
            experience__lte=candidate_experience,
            skills__icontains=candidate_skills,
        )

class ApproveEmployerView(APIView):
    permission_classes=[IsAdminUser]

    def patch(self,request,pk):
        employer=get_object_or_404(Employer,pk=pk)

        employer.is_approved=True
        employer.save()

        AuditLog.objects.create(
        admin=request.user,
        action=f"Approved employer: {employer.company_name}"
        )

        return Response(
            {"message":"Employer approved Successfully"},
            status=status.HTTP_200_OK
        )
    
class BlockUserView(APIView):
    permission_classes=[IsAdminUser]

    def patch(self,request,pk):
        user=get_object_or_404(CustomUser,pk=pk)

        user.is_blocked = not user.is_blocked
        user.save()

        AuditLog.objects.create(
        admin=request.user,
        action=f"Blocked user: {user.username}"
)

        return Response(
            {
                "message": "User blocked"
                if user.is_blocked
                else "User unblocked"
            },
            status=status.HTTP_200_OK,
        )

class AdminJobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAdminUser]


class AdminJobDeleteView(generics.DestroyAPIView):
    queryset = Job.objects.all()
    permission_classes = [IsAdminUser]

    def perform_destroy(self, instance):

        AuditLog.objects.create(
            admin=self.request.user,
            action=f"Deleted job: {instance.title}"
        )

        instance.delete()


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        data = {
            "total_users": CustomUser.objects.count(),
            "total_employers": Employer.objects.count(),
            "total_candidates": Candidate.objects.count(),
            "total_jobs": Job.objects.count(),
            "total_applications": Application.objects.count(),
        }

        return Response(data)

class UserGrowthView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()

        data = {
            "today": CustomUser.objects.filter(
                date_joined__date=today
            ).count(),

            "last_7_days": CustomUser.objects.filter(
                date_joined__date__gte=today - timedelta(days=7)
            ).count(),

            "last_30_days": CustomUser.objects.filter(
                date_joined__date__gte=today - timedelta(days=30)
            ).count(),
        }

        return Response(data)

class JobActivityView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        data = {
            "total_jobs": Job.objects.count(),
            "open_jobs": Job.objects.filter(status=True).count(),
            "closed_jobs": Job.objects.filter(status=False).count(),
            "featured_jobs": Job.objects.filter(is_featured=True).count(),
        }

        return Response(data)

class FlagJobView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        job.is_flagged = True
        job.save()

        AuditLog.objects.create(
        admin=request.user,
        action=f"Flagged job: {job.title}"
)

        return Response({
            "message": "Job flagged successfully."
        })

class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all().order_by("-created_at")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]