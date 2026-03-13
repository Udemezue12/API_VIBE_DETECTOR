from secrets import token_hex

from django_bolt import BoltAPI, JSON, Request
from .csrf_security import CSRFSecurity

api = BoltAPI(django_middleware=True)


@api.get("/csrf", tags=["CSRF TOKEN"])
async def get_csrf_token(request: Request):
    csrf_token = token_hex(32)

    response = JSON({
        "csrf_token": csrf_token
    })

    response.set_cookie(
        name="csrf_token",
        value=csrf_token,
        httponly=False,  # JS must read it
        secure=False,    # True in production
        samesite="Lax",
        max_age=3600
    )

    return response