from rest_framework import serializers
from .models import Employer,Candidate,Job,Application

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Employer
        fields="__all__"
        read_only_fields=["user"]

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Candidate
        fields="__all__"
        read_only_fields=["user"]

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model=Job
        fields="__all__"
        read_only_fields = ["employer"]

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(
        source="candidate.user.first_name",
        read_only=True
    )
    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "candidate_name",
            "candidate_email",
            "job",
            "status",
            "applied_at",
            "resume_snapshot",
        ]

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=["status"]