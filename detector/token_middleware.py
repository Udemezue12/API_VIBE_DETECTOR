import logging
from django.http import JsonResponse
from django_bolt.middleware import Middleware
from django_bolt import Request, Response

class CookieToAuthHeaderMiddleware(Middleware):
    def __init__(self, get_response:Response):
        self.get_response = get_response

    def __call__(self, request: Request):
        
        if not request.headers.get("Authorization"):
            token = request.cookies.get("access_token")
            if token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return self.get_response(request)

    def process_request(self, request: Request):
        return None