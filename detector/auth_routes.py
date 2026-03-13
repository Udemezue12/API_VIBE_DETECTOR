from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django_bolt import BoltAPI, Request
from django_bolt.auth import (
    AllowAny,
    InMemoryRevocation,
    JWTAuthentication,
)
from django_bolt.middleware import rate_limit

from detector.services.user_services import UserService

from .schemas import (
    ResetPasswordSchema,
    ReVerifySchema,
    UserLoginSchema,
    UserRegisterSchema,
    VerifyEmailSchema,
)
from .security_verification import UserVerification

api = BoltAPI(django_middleware=True)
User = get_user_model()

#For Production
# django_store = DjangoCacheRevocation(
#     cache_alias="default",
#     key_prefix="revoked_tokens:"
# ) 

# # For development
memory_store = InMemoryRevocation() 
jwt_auth = JWTAuthentication(revocation_store=memory_store)


@api.post(
    "/register",
    summary="User Registration",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def register(data: UserRegisterSchema, request):
    return await UserService().register(request, data)


@api.post(
    "/login", summary="User Login", tags=["User Authentication"], guards=[AllowAny()]
)
@rate_limit(rps=3, burst=5)
async def login(data: UserLoginSchema, request):
    return await UserService().login(request, data)


@csrf_exempt
@api.post(
    "/logout",
    summary="User Logout",
    tags=["User Authentication"],
    auth=[jwt_auth],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def logout(request: Request):
    return await UserService().logout(request, memory_store)


@api.post(
    "/refresh_token",
    summary="User Refresh Token",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def refresh_token(request: Request):
    return await UserService().refresh(request)


@api.post(
    "/verify-email",
    summary="User Email Verification",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def verify_email(data: VerifyEmailSchema):
    return await UserVerification().verify_email(token=data.token, otp=data.otp)


@api.post(
    "/resend-email-verification-link",
    summary="User Resend Email Verification Link",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def resend_email_link(data: ReVerifySchema):
    return await UserVerification().resend_verification_link(email=data.email)


@api.post(
    "/forgot-password",
    summary="User Forgot Password",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def forgot_password(data: ReVerifySchema):
    return await UserService().forgot_password(data)


@api.post(
    "/reset--password",
    summary="User Reset Password",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def reset_password(data: ResetPasswordSchema):
    return await UserService().reset_password(data)


@api.post(
    "/resend-password-reset-link",
    summary="User Resend Password Reset Link",
    tags=["User Authentication"],
    guards=[AllowAny()],
)
@rate_limit(rps=3, burst=5)
async def resend_password_reset_link(data: ReVerifySchema):
    return await UserVerification().resend_password_reset_link(email=data.email)
