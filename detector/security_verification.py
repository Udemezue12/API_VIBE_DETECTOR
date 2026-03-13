

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from django_bolt.exceptions import HTTPException
from redis.asyncio import Redis

from vibe_detector.celery_app import app as task_app
from .function_breaker import breaker
from .env import (
    REDIS_URL,
    RESET_PASSWORD_SALT,
    RESET_SECRET_KEY,
    VERIFY_EMAIL_SALT,
    VERIFY_EMAIL_SECRET_KEY,
)
from django.contrib.auth import get_user_model


from detector.repo_deps import CRUDDependencies, ExistingDependencies
from .security_generate import user_generate
from detector.repo.auth_repo import AuthRepo
User = get_user_model()
reset_serializer = URLSafeTimedSerializer(RESET_SECRET_KEY or "")
verify_serializer = URLSafeTimedSerializer(VERIFY_EMAIL_SECRET_KEY or "")
resend_tracker: dict[str, dict] = {}
redis = Redis.from_url(REDIS_URL, decode_responses=True)


class UserVerification:
    def __init__(self):
        self.repo = CRUDDependencies()
        self.check = ExistingDependencies()
        self.auth_repo=AuthRepo()
       

    async def verify_reset_token(
        self, token: str, expiration: int = 3600
    ) -> str | None:
        try:
            email = reset_serializer.loads(
                token, salt=RESET_PASSWORD_SALT, max_age=expiration
            )
            return email
        except (SignatureExpired, BadSignature):
            return None

    async def verify_verify_token(
        self, token: str, expiration: int = 3600
    ) -> str | None:
        try:
            email = verify_serializer.loads(
                token, salt=VERIFY_EMAIL_SALT, max_age=expiration
            )
            return email
        except (SignatureExpired, BadSignature):
            return None

    async def verify_otp(self, otp: str) -> str:
        async def handler():
            async for key in redis.scan_iter(match="otp:*"):
                stored = await redis.get(key)
                if stored == otp:
                    await redis.delete(key)
                    return key.split(":")[1]
            return None

        return await breaker.call(handler)

    async def resend_verification_link(
        self, email: str
    ):
        email_payload = email.strip().lower()
        user = await self.repo.aget_object(model=User, email=email_payload)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.is_verified:
            raise HTTPException(status_code=400, detail="Email already verified.")

        otp = await user_generate.generate_otp(email)
        token = await user_generate.generate_verify_token(email)
        name = f"{user.last_name} {user.first_name}"
        task_app.send_task(
            "send_verify_email_notification",
            args=[str(user.phone_number), str(user.email),
                  str(otp), str(name), str(token)]

        )
        return {"message": "Verification Link via your email resent."}

    async def resend_password_reset_link(
        self, email: str,
    ):
        email_payload = email.strip().lower()
        user = await self.repo.aget_object(model=User, email=email_payload)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        otp = await user_generate.generate_otp(email)
        token = await user_generate.generate_reset_token(email)
        name = f"{user.last_name} {user.first_name}"

        task_app.send_task(
            "send_password_reset_notification",
            args=[str(user.phone_number), str(user.email),
                  str(otp), str(name), str(token)]

        )
        return {"message": "Password reset link via your email resent successfully."}

    async def verify_email(self, otp: str | None = None, token: str | None = None):
        if otp and otp.strip():
            email = await self.verify_otp(otp)
        elif token:
            email = await self.verify_verify_token(token)
        else:
            raise HTTPException(status_code=400,
                            detail="No verification data provided")
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification token",
            )
        user = await self.repo.aget_object(model=User, email=email)
        user.is_verified = True
        # user_id = user.id
        await user.asave()
        # await self.cache.delete_from_cache(f"users::{user_id}")
        return {"message": "Email verified successfully"}
