from django.http import JsonResponse

class RoleMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self, request):
        #example check authenticated users
        print("Middleware executed")

        response=self.get_response(request)

        return response
    

