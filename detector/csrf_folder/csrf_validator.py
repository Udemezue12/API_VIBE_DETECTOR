from django_bolt.exceptions import HTTPException
from django_bolt import Request
from .csrf_security import CSRFSecurity


class CSRFValidator:

    async def validate(self, request:Request):

        header_token = request.headers.get("X-CSRF-TOKEN")
        cookie_token = request.cookies.get("csrf_token")
        session_token=request.session.get("csrf_token")
        print("---- CSRF DEBUG ----")
        print("All cookies:", request.cookies)
        print("Header token:", header_token)
        print("Cookie token:", cookie_token)
        print("Session token:", session_token)
        print("--------------------")
        

        if not cookie_token:
            raise HTTPException(403, "Missing CSRF token")

        
        if header_token and header_token != cookie_token:
            raise HTTPException(403, "CSRF token mismatch")

        if not CSRFSecurity.verify_csrf_token(cookie_token):
            raise HTTPException(403, "Invalid CSRF token")

        return True