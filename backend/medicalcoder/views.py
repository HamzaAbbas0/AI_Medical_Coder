from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .serializers import (
    UserRegisterSerializer, UserSerializer,
    PasswordChangeSerializer, EmailUpdateSerializer, PasswordResetSerializer, MedicalDocumentSerializer
)
from .api_response import ok, fail
from .models import MedicalDocument
from .serializers import MedicalDocumentSerializer
from .code_generation import process_icd_codes
from rest_framework.parsers import MultiPartParser, FormParser
import os
import tempfile
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

User = get_user_model()

# -------------------------------------------------------------------------
# USER REGISTRATION
# -------------------------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            payload = UserSerializer(user).data
            return ok(
                data=payload,
                message="User registered successfully.",
                code="USER_REGISTERED",
                http_status=status.HTTP_201_CREATED
            )
        except Exception as exc:
            errors = serializer.errors if hasattr(serializer, "errors") else {}
            detail_msg = str(errors or exc)
            # Highlight duplicate user errors
            if "username" in errors:
                message = "Username already exists. Please choose a different one."
            elif "email" in errors:
                message = "Email already registered. Try logging in or use another email."
            elif "password" in errors:
                message = "Password does not meet security criteria."
            else:
                message = "Failed to register user. Please verify your details."
            return fail(
                message=message,
                code="USER_CREATE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=detail_msg
            )

# -------------------------------------------------------------------------
# LOGIN (Fully controlled JSON error handling)
# -------------------------------------------------------------------------
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Check username existence first
        user_qs = User.objects.filter(username=username)
        if not user_qs.exists():
            raise AuthenticationFailed("No account found with this username.")

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed("Incorrect password. Please try again.")

        # All good → continue with normal token generation
        data = super().validate(attrs)
        data.update({"user": UserSerializer(user).data})
        return data


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return ok(
                data=serializer.validated_data,
                message="Login successful.",
                code="USER_LOGGED_IN",
                http_status=status.HTTP_200_OK
            )

        except AuthenticationFailed as e:
            # Handle wrong username or password
            message = str(e)
            if "username" in message:
                message = "No account found with this username."
            elif "password" in message:
                message = "Incorrect password. Please try again."

            return fail(
                message=message,
                code="LOGIN_FAILED",
                http_status=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

        except serializers.ValidationError as e:
            return fail(
                message="Invalid credentials format.",
                code="LOGIN_VALIDATION_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=e.detail
            )

        except Exception as e:
            return fail(
                message="Unexpected error during login.",
                code="LOGIN_ERROR",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


# -------------------------------------------------------------------------
# CURRENT USER VIEW (Optional)
# -------------------------------------------------------------------------
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return ok(
            data=self.get_serializer(self.get_object()).data,
            message="Fetched current user successfully.",
            code="USER_PROFILE"
        )



# -------------------------------------------------------------------------
# PASSWORD CHANGE
# -------------------------------------------------------------------------
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return ok(message="Password updated successfully.", code="PASSWORD_UPDATED")
        except Exception as e:
            errors = getattr(e, "detail", None) or str(e)
            message = "Failed to update password."
            if "Incorrect password" in str(errors):
                message = "Current password is incorrect."
            return fail(
                message=message,
                code="PASSWORD_UPDATE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(errors)
            )

# -------------------------------------------------------------------------
# FORGOT PASSWORD (Reset)
# -------------------------------------------------------------------------
class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return ok(
                message="Password reset successfully. You can now log in with your new password.",
                code="PASSWORD_RESET_SUCCESS"
            )
        except Exception as e:
            errors = serializer.errors if hasattr(serializer, "errors") else {}
            if "email" in errors:
                message = "No account found with this email."
            elif "new_password" in errors:
                message = "Password does not meet the security criteria."
            else:
                message = "Failed to reset password. Please check your details."
            return fail(
                message=message,
                code="PASSWORD_RESET_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(errors)
            )

# -------------------------------------------------------------------------
# EMAIL UPDATE
# -------------------------------------------------------------------------
class EmailUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            s = EmailUpdateSerializer(data=request.data, context={"request": request})
            s.is_valid(raise_exception=True)
            s.save()
            return ok(message="Email updated successfully.", code="EMAIL_UPDATED")
        except Exception as e:
            errors = getattr(e, "detail", None) or str(e)
            if "email" in str(errors):
                message = "This email is already in use."
            else:
                message = "Failed to update email address."
            return fail(
                message=message,
                code="EMAIL_UPDATE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(errors)
            )

# -------------------------------------------------------------------------
#  MEDICAL DOCUMENT CRUD VIEWS
# -------------------------------------------------------------------------

class MedicalDocumentUploadProcessView(generics.GenericAPIView):
    """
    Accepts a file upload (multipart/form-data, key='file'),
    saves it to a temp file, runs the AI pipeline, deletes the temp file,
    and stores only the original filename in DB.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return fail(
                message="No file provided. Use multipart/form-data with key 'file'.",
                code="NO_FILE",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        original_name = uploaded.name
        suffix = os.path.splitext(original_name)[1] or ".pdf"

        # Write to a guaranteed temp path
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = tmp.name
                for chunk in uploaded.chunks():
                    tmp.write(chunk)

            # Run existing pipeline on the temp file
            ai_result = process_icd_codes(tmp_path)
            if ai_result.get("status") != "success":
                return fail(
                    message="AI code generation failed",
                    code="AI_PROCESS_FAILED",
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ai_result.get("message")
                )

            # Parse outputs safely
            icd_parent = ai_result.get("icd_parent_codes", {})  # {"icd_codes": [...]}
            icd_specified = ai_result.get("icd_codes", {})      # {"icd_codes": [...] or raw text JSON}
            cpt_data = ai_result.get("cpt_codes", {})

            # Extract CPT codes list
            cpt_only = cpt_data.get("cpt_codes", [])
            
            # Extract HCPCS codes separately
            hcpcs_data = cpt_data.get("hcpcs_codes", [])
            
            # Extract modifiers from each CPT code entry
            modifiers = []
            for item in cpt_only:
                if item.get("modifier"):
                    modifiers.append({
                        "code": item.get("modifier"),
                        "description": item.get("description_modifier", "")
                    })

            # Store only the original filename (not server path)
            doc = MedicalDocument.objects.create(
                user=request.user,
                file_path=original_name,
                icd_parent_codes=icd_parent,
                icd_specified_codes=icd_specified,
                cpt_codes={"cpt": cpt_only},
                modifiers={"Modifiers": modifiers},
                hcpcs_codes=hcpcs_data,
            )

            payload = MedicalDocumentSerializer(doc).data
            return ok(
                data=payload,
                message="Uploaded, processed by AI, and removed from server",
                code="DOCUMENT_UPLOADED_PROCESSED",
                http_status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return fail(
                message="Failed to process uploaded document",
                code="UPLOAD_PROCESS_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        finally:
            # Ensure the temp file is removed no matter what
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


class MedicalDocumentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all medical documents belonging to the authenticated user.
    POST: Create a new medical document entry.
    """
    serializer_class = MedicalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MedicalDocument.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return ok(
                data=serializer.data,
                message="Fetched user medical documents",
                code="DOCUMENT_LIST"
            )
        except Exception as e:
            return fail(
                message="Failed to fetch documents",
                code="DOCUMENT_LIST_ERROR",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # -----------------------------------------------------------------
            # 1️⃣  Extract file path from request
            # -----------------------------------------------------------------
            file_path = serializer.validated_data.get("file_path")
            user = request.user

            # -----------------------------------------------------------------
            # 2️⃣  Run the AI medical coding pipeline
            # -----------------------------------------------------------------
            print(f"[AI Pipeline] Processing file: {file_path}")
            ai_result = process_icd_codes(file_path)

            if ai_result.get("status") != "success":
                return fail(
                    message="AI code generation failed",
                    code="AI_PROCESS_FAILED",
                    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ai_result.get("message")
                )
            print(ai_result, "##########################################################")

            # -----------------------------------------------------------------
            # 3️⃣  Parse results
            # -----------------------------------------------------------------
            icd_parent = ai_result.get("icd_parent_codes", {})
            icd_specified = ai_result.get("icd_codes", {})
            cpt_data = ai_result.get("cpt_codes", {})

            # Extract CPT codes list
            cpt_only = cpt_data.get("cpt_codes", [])
            
            # Extract HCPCS codes separately
            hcpcs_data = cpt_data.get("hcpcs_codes", [])
            
            # Extract modifiers from each CPT code entry
            modifiers = []
            for item in cpt_only:
                if item.get("modifier"):
                    modifiers.append({
                        "code": item.get("modifier"),
                        "description": item.get("description_modifier", "")
                    })

            # -----------------------------------------------------------------
            # 4️⃣  Save to DB
            # -----------------------------------------------------------------
            document = MedicalDocument.objects.create(
                user=user,
                file_path=file_path,
                icd_parent_codes=icd_parent,
                icd_specified_codes=icd_specified,
                cpt_codes={"cpt": cpt_only},
                modifiers={"Modifiers": modifiers},
                hcpcs_codes=hcpcs_data,
            )

            payload = self.get_serializer(document).data

            # -----------------------------------------------------------------
            # 5️⃣  Return success response
            # -----------------------------------------------------------------
            return ok(
                data=payload,
                message="Medical document processed and codes generated successfully",
                code="DOCUMENT_CREATED",
                http_status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return fail(
                message="Failed to process or create document",
                code="DOCUMENT_CREATE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

class MedicalDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific medical document.
    PUT/PATCH: Update codes (e.g., after AI generation).
    DELETE: Remove a document.
    """
    serializer_class = MedicalDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MedicalDocument.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return ok(
                data=serializer.data,
                message="Medical document details retrieved",
                code="DOCUMENT_DETAIL"
            )
        except Exception as e:
            return fail(
                message="Failed to retrieve document",
                code="DOCUMENT_DETAIL_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return ok(
                data=serializer.data,
                message="Medical document updated",
                code="DOCUMENT_UPDATED"
            )
        except Exception as e:
            return fail(
                message="Failed to update document",
                code="DOCUMENT_UPDATE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return ok(
                data=None,
                message="Medical document deleted",
                code="DOCUMENT_DELETED"
            )
        except Exception as e:
            return fail(
                message="Failed to delete document",
                code="DOCUMENT_DELETE_ERROR",
                http_status=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

class MedicalDocumentUploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
 
            # Save temporarily to disk
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, uploaded_file.name)
 
            with open(file_path, 'wb+') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
 
            # Run HIPAA + code extraction pipeline
            result = process_icd_codes(file_path)
 
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)