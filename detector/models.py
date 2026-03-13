import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import UserRole, ScanStatus


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.username)


class WebsiteScanResult(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    url = models.URLField()
    vibe_score = models.FloatField()
    is_vibecoded = models.BooleanField(default=False)
    status = models.CharField(
        choices=ScanStatus,null=False
    )

    detected_framework = models.CharField(max_length=100, null=True, blank=True)

    ai_patterns = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.url)


class GithubScanResult(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    repo_url = models.URLField()
    vibe_score = models.FloatField()
    is_vibecoded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    signals = models.JSONField(default=dict)
    status = models.CharField(choices=ScanStatus, null=False)

    def __str__(self):
        return str(self.repo_url)


class BlacklistedToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    token = models.CharField(max_length=512, unique=True)

    blacklisted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "blacklisted_tokens"
        indexes = [
            models.Index(fields=["token"], name="idx_blacklisted_token"),
        ]

    def __str__(self):
        return str(self.token)
