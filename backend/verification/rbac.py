from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsStaffOrFactChecker(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name='FactChecker').exists()


class CanVerifyClaim(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(
            name__in=['FactChecker', 'Editor']
        ).exists()


class CanManageTrends(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name='TrendManager').exists()


class CanViewAnalytics(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(
            name__in=['Analyst', 'FactChecker', 'Editor']
        ).exists()
