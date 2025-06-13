from rest_framework import permissions

def user_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
    

class IsInGroup(permissions.BasePermission):
    group_name = None

    def has_permission(self, request, view):
        return user_in_group(request.user, self.group_name)

class IsFarmer(IsInGroup):
    group_name = 'farmer'

class IsLabor(IsInGroup):
    group_name = 'labor'

class IsTractor(IsInGroup):
    group_name = 'tractor'    

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser                