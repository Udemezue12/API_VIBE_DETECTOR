import re
from typing import Annotated, Optional

import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_bolt.serializers import Email as EmailStr
from django_bolt.serializers import Meta as constr
from django_bolt.serializers import Serializer as Schema
from django_bolt.serializers import field_validator, model_validator


class UserRegisterSchema(Schema):
    username: Annotated[str, constr(min_length=4, max_length=20)]
    first_name: Annotated[str, constr(min_length=4, max_length=20)]
    last_name: Annotated[str, constr(min_length=4, max_length=20)]
    password: Annotated[str, constr(min_length=6)]
    confirm_password: Annotated[str, constr(min_length=6)]
    email: str
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str):
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number. Use full international format.")
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        except Exception:
            raise ValueError("Invalid phone number format. Use e.g. +2348012345678")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        try:
            validate_email(v)
        except ValidationError:
            raise ValueError("Invalid email format")

        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must only contain letters and spaces")
        return v

    @model_validator(mode="after")
    def validate_confirm_password(self):
        if self.password and self.confirm_password != self.password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        errors = []
        if len(v) < 7:
            errors.append("≥7 characters")
        if not re.search(r"[A-Z]", v):
            errors.append("uppercase letter")
        if not re.search(r"[a-z]", v):
            errors.append("lowercase letter")
        if not re.search(r"\d", v):
            errors.append("number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            errors.append("special character")
        if errors:
            raise ValueError("Password must contain: " + ", ".join(errors))
        return v


class UserOut(Schema):
    id: Optional[int] = None
    username: str
    last_name: str
    first_name: str
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class UserLoginSchema(Schema):
    username: str
    password: str

    class Config:
        from_attributes = True


class VerifyEmailSchema(Schema):
    otp: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_token_or_otp(cls, values):
        token = values.get("token")
        otp = values.get("otp")
        if not token and not otp:
            raise ValueError("Either token or otp must be provided")
        return values


class ReVerifySchema(Schema):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        try:
            validate_email(v)
        except ValidationError:
            raise ValueError("Invalid email format")

        return v


class ResetPasswordSchema(Schema):
    token: Optional[str] = None
    otp: Optional[str] = None
    new_password: str

    @model_validator(mode="before")
    @classmethod
    def validate_token_or_otp(cls, values):
        token = values.get("token")
        otp = values.get("otp")
        if not token and not otp:
            raise ValueError("Either token or otp must be provided")
        return values
