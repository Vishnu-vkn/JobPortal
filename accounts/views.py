#sign-up api

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer

class SignupView(APIView):
    def post(self,request):
        serializer=SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message":"User Registered Successfully"},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            refresh_token=request.data["refresh"]
            token=RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message":"Logout Successful"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"error":"Invalid Token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class AdminTestView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]
    def get(self,request):
        print("View Executed")
        return Response({
            "message":"Welcome Admin",
            "user":request.user.username,
            "role":request.user.role
        })
