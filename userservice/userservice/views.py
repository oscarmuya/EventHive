from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from .permissions import IsOrganizer
from .models import Organization
from rest_framework.permissions import IsAuthenticated


def generate_tokens_for_user(user):
    serializer = MyTokenObtainPairSerializer()
    token = serializer.get_token(user)

    return {
        "refresh": str(token),
        "access": str(token.access_token),
    }


def set_refresh_token_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="Lax",  #! Or 'Strict'
        secure=False,  #! Set to True in production
    )


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")
            set_refresh_token_cookie(response, refresh_token)
            response.data = {
                "access": access_token,
                "expires_in": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            }
        return response


class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token
        else:
            return Response(
                {"error": "Please re-authenticate", "code": "refresh_token_not_found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get("access")
            new_refresh_token = response.data.get("refresh")
            if new_refresh_token:
                set_refresh_token_cookie(response, refresh_token)
            response.data = {
                "access": access_token,
                "expires_in": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            }
        return response


class OrganizationView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizer]

    def post(self, request):
        email = request.data.get("email")
        organization_id = request.auth.get("organization_id")

        if not email or not organization_id:
            return Response(
                {"error": "Email and organization_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get organization
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get user
        try:
            new_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if user is already in another organization
        try:
            existing_organization = Organization.objects.get(organizers=new_user)
            if existing_organization != organization:
                return Response(
                    {"error": "User is already in another organization"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Organization.DoesNotExist:
            pass
        new_user.groups.add(Group.objects.get_or_create(name="organizers"))
        new_user.groups.remove(Group.objects.get_or_create(name="users"))

        organization.organizers.add(new_user)
        organization.save()

        return Response(
            {"message": "User added to organization"}, status=status.HTTP_200_OK
        )


class RegisterUserView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if not email or not password:
                return Response(
                    {"error": "Email, password are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "User with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_group, _ = Group.objects.get_or_create(name="users")

            user = User.objects.create_user(
                username=email, email=email, password=password
            )

            user.groups.add(user_group)

            serializer = UserSerializer(user)
            tokens = generate_tokens_for_user(user)

            response = Response(
                {
                    "user": serializer.data,
                    "access": tokens.access,
                    "expires_in": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                },
                status=status.HTTP_201_CREATED,
            )
            set_refresh_token_cookie(response, tokens.refresh)

            return response

        except Exception as e:
            print(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
