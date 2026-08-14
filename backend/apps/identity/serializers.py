"""
Phase 05 Identity serializers.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=150)
    preferred_locale = serializers.ChoiceField(
        choices=[("fa-IR", "fa-IR"), ("en-US", "en-US")], default="fa-IR"
    )
    invitation_token = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "display_name",
            "preferred_locale",
            "preferred_unit",
            "timezone",
            "is_platform_admin",
            "created_at",
        ]
        read_only_fields = ["id", "email", "is_platform_admin", "created_at"]


class CurrentUserResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    memberships = serializers.ListField(child=serializers.DictField(), required=False)


class UpdateMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["display_name", "preferred_locale", "preferred_unit", "timezone"]


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
