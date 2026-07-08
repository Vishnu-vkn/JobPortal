from rest_framework import serializers
from .models import CustomUser

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=["username","email","phone","password"]
        extra_kwargs={
            "password":{"write_only":True}
        }

    def create(self,validated_data):
        return CustomUser.objects.create_user(**validated_data)