from django.contrib import admin
from .models import User, MedicalDocument

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_active", "is_staff")
    search_fields = ("username", "email")

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file_path", "created_at")
    search_fields = ("file_path", "user__username")
    list_filter = ("created_at",)