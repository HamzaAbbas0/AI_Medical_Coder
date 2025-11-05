from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from .models import MedicalDocument

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        pwd = validated_data.pop("password", "")[:72]
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if not check_password(attrs["current_password"], user.password):
            raise serializers.ValidationError({"current_password": "Incorrect password."})
        password_validation.validate_password(attrs["new_password"], user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"][:72])
        user.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get("email")
        new_password = attrs.get("new_password")
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"email": "No account found with this email."})

        # Strong password validation (same as Django built-in)
        password_validation.validate_password(new_password, user)
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"][:72])
        user.save()
        return user


class EmailUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.email = self.validated_data["email"]
        user.save()
        return user


class MedicalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDocument
        fields = [
            "id",
            "user",
            "file_path",
            "icd_parent_codes",
            "icd_specified_codes",
            "cpt_codes",
            "modifiers",
            "hcpcs_codes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
