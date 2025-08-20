from rest_framework.permissions import BasePermission


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
