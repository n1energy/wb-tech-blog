from rest_framework import permissions


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            obj.user == request.user or
            request.user.is_staff
        )

# class IsMasterOrReadOnly(BasePermission):
#     """
#     The request is authenticated as a user, or is a read-only request.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         return bool(
#             request.method in SAFE_METHODS or
#             request.user and
#             request.user.is_authenticated and
#             (
#                     obj.master == request.user or
#                     request.user.is_staff
#             )
#         )
