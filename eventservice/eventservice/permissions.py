from rest_framework.permissions import BasePermission
from utils.checks import is_internal_request


class IsOrganizer(BasePermission):
    """
    Allows access only to users with the 'organizer' role.
    """

    def has_permission(self, request, _):
        print(request.auth.get("roles", ""))
        roles_str = request.auth.get("roles", "")
        return "organizers" in roles_str.split(",")


class IsUser(BasePermission):
    """
    Allows access only to users with the 'boss' role.
    """

    def has_permission(self, request, _):
        roles_str = request.auth.get("roles", "")
        return "users" in roles_str.split(",")


class IsInternalRequest(BasePermission):
    """
    Allows access only to internal requests.
    """

    def has_permission(self, request, _):
        # Check if the request is from an internal service
        return is_internal_request(request)
