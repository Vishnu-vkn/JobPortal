from rest_framework import serializers
from .models import CustomUser
from jobportal.models import Employer,Candidate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=["username","email","phone","password","role"]
        extra_kwargs={
            "password":{"write_only":True}
        }

    def create(self,validated_data):
        user= CustomUser.objects.create_user(**validated_data)
        if user.role == CustomUser.Role.EMPLOYER:
            Employer.objects.create(user=user)

        elif user.role == CustomUser.Role.CANDIDATE:
            Candidate.objects.create(user=user)

        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        if self.user.is_blocked:
            raise serializers.ValidationError(
                "Your account has been blocked."
            )

        return data
