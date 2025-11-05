from django.urls import path
from .views import PasswordResetView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView, MeView, PasswordChangeView, EmailUpdateView,
    MedicalDocumentListCreateView, MedicalDocumentDetailView, MedicalDocumentUploadProcessView, MedicalDocumentUploadView, CustomLoginView
)

urlpatterns = [
    # Auth (JWT)
    path("auth/login/", CustomLoginView.as_view(), name="custom_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # User profile endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/password/", PasswordChangeView.as_view(), name="password_change"),
    path("auth/email/", EmailUpdateView.as_view(), name="email_update"),
    
    # Medical Document endpoints
    path("medical-documents/", MedicalDocumentListCreateView.as_view(), name="medicaldocument_list_create"),
    path("medical-documents/<int:pk>/", MedicalDocumentDetailView.as_view(), name="medicaldocument_detail"),
    # path("medical-documents/upload/", MedicalDocumentUploadProcessView.as_view(), name="medicaldocument_upload"),
    path('medical-documents/upload/', MedicalDocumentUploadView.as_view(), name='medical-doc-upload'),
]
