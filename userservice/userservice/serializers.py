from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Organization


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        try:
            organization = Organization.objects.get(organizers=user)
            token["organization_id"] = organization.pk
        except Organization.DoesNotExist:
            pass

        user_groups = user.groups.all()
        token["roles"] = ",".join([group.name for group in user_groups])

        return token


class UserSerializer(serializers.ModelSerializer):
    # 1. Define the new field as a SerializerMethodField
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "roles")

    def get_roles(self, obj):
        """
        obj is the User instance.
        Returns a comma-separated string of group names.
        """
        user_groups = obj.groups.all()
        group_names = [group.name for group in user_groups]
        return ",".join(group_names)
