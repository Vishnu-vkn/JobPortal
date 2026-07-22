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
    class Meta:
        model=Application
        fields="__all__"
        read_only_fields=(
            "candidate",
            "job",
            "resume_snapshot",
            "status",
            "applied_at"
        )

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=["status"]