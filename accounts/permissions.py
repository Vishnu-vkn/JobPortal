from rest_framework.permissions import BasePermission
from .models import CustomUser

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role==CustomUser.Role.ADMIN
    
class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return  ( request.user.role==CustomUser.Role.EMPLOYER
        or request.user.is_staff
        )
    
class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return request.user.role==CustomUser.Role.CANDIDATE