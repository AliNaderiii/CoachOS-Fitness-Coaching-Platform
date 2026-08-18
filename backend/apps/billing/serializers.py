from rest_framework import serializers

from .models import BillingRoleAssignment, Plan, PlanEntitlement, Price


class PlanEntitlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanEntitlement
        fields = ["key", "kind", "enabled", "integer_limit", "label_en", "label_fa"]


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            "id",
            "code",
            "currency",
            "currency_exponent",
            "unit_amount_minor",
            "interval",
            "trial_days",
            "grace_period_days",
        ]


class PlanSerializer(serializers.ModelSerializer):
    entitlements = PlanEntitlementSerializer(many=True, read_only=True)
    prices = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id",
            "code",
            "name_en",
            "name_fa",
            "description_en",
            "description_fa",
            "included_athletes",
            "entitlements",
            "prices",
        ]

    def get_prices(self, plan):
        return PriceSerializer(plan.prices.filter(is_active=True), many=True).data


class CheckoutInputSerializer(serializers.Serializer):
    price_id = serializers.CharField(max_length=36)
    locale = serializers.ChoiceField(choices=["fa-IR", "en-US"])


class PortalInputSerializer(serializers.Serializer):
    locale = serializers.ChoiceField(choices=["fa-IR", "en-US"])


class BillingAdminInputSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=36)


class BillingRoleAssignmentSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source="user.id", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = BillingRoleAssignment
        fields = ["id", "user_id", "display_name", "role", "granted_at"]
