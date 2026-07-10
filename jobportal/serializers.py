from rest_framework import serializers
from .models import Employer,Candidate

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