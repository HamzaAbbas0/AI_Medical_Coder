from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models
import os

class User(AbstractUser):
    """
    Custom user model. You can later enforce email uniqueness or add fields.
    For now it's a thin wrapper around AbstractUser to keep migration easy.
    """
    # example future fields:
    # organization = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.username
    

class MedicalDocument(models.Model):
    """
    Stores each medical document processed by the AI Medical Coder pipeline.
    Links to the User who created/uploaded it and stores all generated codes.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_documents"
    )

    file_path = models.CharField(max_length=512)

    # JSON fields for various code outputs
    icd_parent_codes = models.JSONField(default=dict)
    icd_specified_codes = models.JSONField(default=dict)
    cpt_codes = models.JSONField(default=dict)
    modifiers = models.JSONField(default=dict)
    hcpcs_codes = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {os.path.basename(self.file_path)}"
    



