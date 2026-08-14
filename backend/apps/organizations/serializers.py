from rest_framework import serializers

from .models import Invitation, Location, Membership, Organization


class CreateOrganizationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    slug = serializers.SlugField(max_length=100)
    primary_location = serializers.DictField(required=False)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "owner_user_id", "settings", "created_at", "archived_at"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "organization_id", "name", "is_primary", "address_line1", "city", "phone"]


class CreateInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES)


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "email", "role", "expires_at", "accepted_at"]


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["id", "user_id", "organization_id", "role", "status", "created_at"]
