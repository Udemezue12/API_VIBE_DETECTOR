from django.db.models import TextChoices


class UserRole(TextChoices):
    USER = "USER", "User"
    ADMIN = "ADMIN", "Admin"
class ScanStatus(TextChoices):
    PENDING="PENDING", "Pending"
    FAILED = "FAILED", "Failed"
    SUCCESSFUL= "SUCCESSFUL", "Successful"
