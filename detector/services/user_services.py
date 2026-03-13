from django.conf import settings
from django.contrib.auth import aauthenticate, alogin, get_user_model
from django.contrib.auth import alogin as django_login
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django_bolt import JSON as JSONResponse
from django_bolt import Depends, Request
from django_bolt.auth import (
    InMemoryRevocation,
    JWTAuthentication,
    create_jwt_for_user,
    get_current_user,
)
from django_bolt.exceptions import HTTPException, Unauthorized
from injector import inject
from jose import ExpiredSignatureError, JWTError, jwt

from detector.env import JWT_SECRET_KEY, SECRET_KEY
from detector.helper import run_sync
from detector.repo.auth_repo import AuthRepo
from vibe_detector.celery_app import app as task_app

from ..csrf_token import validate_csrf
from ..jwt_service import create_access_token, create_refresh_token
from ..repo_deps import CRUDDependencies, ExistingDependencies
from ..security_generate import UserGenerate
from ..security_verification import UserVerification

User = get_user_model()


class UserService:
    @inject
    def __init__(
        self,
    ):
        self.deps = CRUDDependencies()
        self.check_existing = ExistingDependencies()
        self.auth_repo = AuthRepo()
        self.generate = UserGenerate()
        self.verification = UserVerification()

        # self.cache = AsyncCacheDependencies()

    async def users(self):
        users = await self.deps.aget_list(model=User)
        return users

    async def register(self, request: Request, data):
        # await self.csrf_validate.validate_csrf(request)
        deps = self.deps
        check_existing = self.check_existing
        username = data.username
        first_name = data.first_name
        password = data.password
        last_name = data.last_name
        email = data.email
        phone_number = data.phone_number
        await check_existing.async_check_existing(
            model=User, raise_error_if_exists=True, email=email, error_field="Email"
        )
        await check_existing.async_check_existing(
            model=User,
            raise_error_if_exists=True,
            username=username,
            error_field="Username",
        )
        await check_existing.async_check_existing(
            model=User,
            raise_error_if_exists=True,
            first_name=first_name,
            error_field="First_Name",
        )
        await check_existing.async_check_existing(
            model=User,
            raise_error_if_exists=True,
            last_name=last_name,
            error_field="Last_Name",
        )
        user = await deps.acreate_object(
            model=User,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_verified=False,
            phone_number=phone_number,
        )
        user.set_password(password)
        await user.asave()
        if user:
            token = await self.generate.generate_reset_token(user.email)
            otp = await self.generate.generate_otp(user.email)
            name = f"{user.last_name} {user.first_name}"
            task_app.send_task(
                "send_verify_email_notification",
                args=[
                    str(user.phone_number),
                    str(user.email),
                    str(otp),
                    str(name),
                    str(token),
                ],
            )
        return {
            "message": "Your registration was successful. Kindly check your email inbox or SMS to complete account verification."
        }

    async def login(self, request: Request, data):
        # await validate_csrf(request)
        username = data.username
        password = data.password
        user = await aauthenticate(username=username, password=password)
        if user is None:
            raise Unauthorized(detail="Invalid credentials")
        token = create_jwt_for_user(user, expires_in=3600)
        access_token = create_access_token(user, expires_in=900)
        refresh_token = create_refresh_token(user, expires_in=86400)

        await django_login(request, user)
        response = JsonResponse(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 900,
            }
        )

        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            samesite="Lax",
            secure=False,
            max_age=900,
        )

        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            samesite="Lax",
            secure=False,
            max_age=86400,
        )

        return response

    async def logout(self, request: Request, store):
        await run_sync(django_logout, request)
        refresh_token = request.cookies.get("refresh_token")
        access_token = request.cookies.get("access_token")
        session_id = request.cookies.get("sessionid")
        
        token_jti = request.context.get("auth_claims", {}).get("jti")

        if refresh_token:
            await self.auth_repo.blacklist_token(refresh_token)
        if access_token:
            await self.auth_repo.blacklist_token(access_token)
        if session_id:
            await self.auth_repo.blacklist_token(session_id)
        if not token_jti:
            pass
        else:
            store.revoke(token_jti)

        res = JsonResponse({"detail": "Logout successful"}, status=200)

        cookies_to_delete = [
            "access_token",
            "refresh_token",
            "csrf_token",
            "session",
            "sessionid",
        ]

        for cookie in cookies_to_delete:
            res.delete_cookie(key=cookie, path="/", samesite="Lax")

        return res

    async def refresh(self, request: Request):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token")
        if await self.auth_repo.is_token_blacklisted(refresh_token):
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            user = await self.deps.aget_object(model=User, pk=user_id)
            access_token = create_jwt_for_user(user, expires_in=900, secret=SECRET_KEY)

            response = JSONResponse({"access_token": access_token})
            response.set_cookie(
                name="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60 * 10,
            )
            return response

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def forgot_password(self, payload):
        user = await self.deps.aget_object(User, email=payload.email)
        if user:
            token = await self.generate.generate_reset_token(user.email)
            otp = await self.generate.generate_otp(user.email)
            name = f"{user.last_name} {user.first_name}"
            task_app.send_task(
                "send_password_reset_notification",
                args=[
                    str(user.phone_number),
                    str(user.email),
                    str(otp),
                    str(name),
                    str(token),
                ],
            )
        return {
            "message": "If the email and phoneNumber exists, a reset link has been sent."
        }

    async def reset_password(self, payload):
        email = None

        if payload.token:
            try:
                email = await self.verification.verify_reset_token(payload.token)
            except Exception:
                pass

        if not email and payload.otp:
            try:
                email = await self.verification.verify_otp(payload.otp)
            except Exception:
                pass

        if not email:
            raise HTTPException(
                status_code=400,
                message="Invalid or expired token",
            )
        user = await self.deps.aget_object(User, email=email)
        if not user:
            raise HTTPException(status_code=404, message="User not found")
        user.set_password(payload.new_password)
        await user.asave()
        return {"message": "Password reset successfully"}
