from datetime import datetime, timedelta

import jwt
from django.conf import settings

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"


def create_access_token(user, expires_in=900):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "type": "access",
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user, expires_in=86400):
    payload = {
        "sub": str(user.id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "type": "refresh",
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)