import logging
from secrets import token_hex

from asgiref.sync import sync_to_async
from django.http import HttpRequest as Request
from django_bolt import BoltAPI, Request, JSON
from django_bolt.exceptions import HTTPException

from detector.csrf_folder.csrf_security import CSRFSecurity

api=BoltAPI(django_middleware=True)
logger = logging.getLogger(__name__)




@api.get("/csrf_token", tags=["CSRF TOKEN"])
async def get_csrf_token(request: Request):
        csrf_token = token_hex(35)
        await sync_to_async(request.session.__setitem__)("csrf_token", csrf_token)
        
        response = JSON({
            "csrf_token":csrf_token
        })
        # response.set_cookie(
        #     name="csrf_token",
        #     value=csrf_token,
        #     httponly=False,
        #     secure=False,
        #     samesite="Lax",
        #     max_age=3600,
        #     path="/"
        # )
        response.headers.setdefault(
    "Set-Cookie",
    f"csrf_token={csrf_token}; HttpOnly; Path=/; Max-Age=3600; samesite=Lax; domain=localhost"
)
        
        return response

async def validate_csrf(request: Request):
        header_token = await sync_to_async(request.headers.get)("X-CSRF-TOKEN")
        session_token = await sync_to_async(request.session.get)("csrf_token")
        cookie_token = await sync_to_async(request.cookies.get)("csrf_token")
        

        print("---- CSRF DEBUG ----")
        print("All cookies:", request.cookies)
        print("Header token:", header_token)
        print("Cookie token:", cookie_token)
        print("Session token:", session_token)
        print("--------------------")
        

        if  not cookie_token:
            raise HTTPException(403, "Missing CSRF token")

        
        if header_token and header_token != cookie_token:
            raise HTTPException(403, "CSRF token mismatch")

        # if not CSRFSecurity.verify_csrf_token(cookie_token):
        #     raise HTTPException(403, "Invalid CSRF token")

        # return True