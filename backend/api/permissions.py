# api/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

class RoleBasedAccess(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            raise NotAuthenticated("Tu dois être connecté pour accéder à cette ressource.")

        if hasattr(view, 'admin_only') and view.admin_only and user.role != 'admin':
            raise PermissionDenied("Accès réservé aux administrateurs.")

        if hasattr(view, 'player_only') and view.player_only and user.role != 'player':
            raise PermissionDenied("Accès réservé aux joueurs.")

        return True
