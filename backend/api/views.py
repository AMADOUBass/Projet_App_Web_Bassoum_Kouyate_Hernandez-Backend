from rest_framework import generics, status
from rest_framework.response import Response
from .permissions import RoleBasedAccess
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import User, Player, SeasonStats, Participation, ReportAdmin, Event
from rest_framework.exceptions import NotAuthenticated
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UnapprovedUserSerializer,
    PlayerProfileSerializer,
    UserSerializer,
    PlayerSerializer,
    SeasonStatsSerializer,
    ParticipationSerializer,
    ReportAdminSerializer,
    EventSerializer

)

from .utils import approve_user

# ------------------------
# User Registration
# ------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# ------------------------
# JWT Login
# ------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ------------------------
# Current User Info
# ------------------------
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# ------------------------
# Player Profile View (for player to update their own profile)
# ------------------------
class PlayerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        try:
            return self.request.user.player_profile
        except Player.DoesNotExist:
            raise NotFound("Profil joueur non trouvé.")


# ------------------------
# List of Unapproved Users (admin only)
# ------------------------
class UnapprovedUserListView(generics.ListAPIView):
    serializer_class = UnapprovedUserSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def get_queryset(self):
        return User.objects.filter(is_approved=False).exclude(role='admin')

# ------------------------
# Approve a User (admin only)
# ------------------------
class ApproveUserView(APIView):
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def post(self, request, user_id):
        user_to_approve = get_object_or_404(User, id=user_id, is_approved=False)
        if user_to_approve.is_active:
            return Response({"detail": "L'utilisateur est déjà actif."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            approve_user(user_to_approve, request.user)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if user_to_approve.role == 'player':
            Player.objects.get_or_create(user=user_to_approve)
        return Response({"detail": f"User {user_to_approve.email} approuvé avec succès."}, status=status.HTTP_200_OK)

# ------------------------
# Admin View of All Players
# ------------------------
class PlayerListView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True
    queryset = Player.objects.all()

# ------------------------
# SeasonStats Serializer
# ------------------------
class SeasonStatsAdminView(generics.ListCreateAPIView):
    queryset = SeasonStats.objects.all()
    serializer_class = SeasonStatsSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

# ------------------------
# SeasonStats Detail View (for admin to update stats)
# ------------------------
class SeasonStatsDetailView(generics.RetrieveUpdateAPIView):
    queryset = SeasonStats.objects.all()
    serializer_class = SeasonStatsSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True
    lookup_field = 'pk'

# ------------------------
#  SeasonStats List View with Filtering (admin only)
# ------------------------
class SeasonStatsAdminListView(generics.ListAPIView):
    serializer_class = SeasonStatsSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def get_queryset(self):
        season = self.request.query_params.get('season')
        if season:
            return SeasonStats.objects.filter(season_year=season)
        return SeasonStats.objects.all()
# ------------------------
# My SeasonStats View (for players to view their own stats)
# ------------------------
class MySeasonStatsView(generics.ListAPIView):
    serializer_class = SeasonStatsSerializer
    permission_classes = [RoleBasedAccess]
    player_only = True

    def get_queryset(self):
        user = self.request.user
        queryset = SeasonStats.objects.filter(player__user=user)

        # 🔍 Filtrage par saison
        season = self.request.query_params.get('season')
        if season:
            queryset = queryset.filter(season_year=season)

        # 🔍 Filtrage par match (même sans classe Match)
        match_id = self.request.query_params.get('match')
        if match_id:
            queryset = queryset.filter(match_id=match_id)

        return queryset
# ------------------------
# Event Participation View (admin only)
# ------------------------
class EventParticipationView(generics.ListAPIView):
    serializer_class = ParticipationSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return Participation.objects.filter(event__id=event_id)


class PlayerParticipationUpdateView(generics.UpdateAPIView):
    serializer_class = ParticipationSerializer
    permission_classes = [RoleBasedAccess]
    player_only = True

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Vous devez être connecté pour accéder à cette ressource.")
        return Participation.objects.filter(player__user=self.request.user)

class ReportAdminCreateView(generics.CreateAPIView):
    serializer_class = ReportAdminSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

class ReportAdminListView(generics.ListAPIView):
    serializer_class = ReportAdminSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True
    queryset = ReportAdmin.objects.all()

class MyParticipationsView(generics.ListAPIView):
    serializer_class = ParticipationSerializer
    permission_classes = [RoleBasedAccess]
    player_only = True

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Vous devez être connecté pour accéder à cette ressource.")
        return Participation.objects.filter(player__user=self.request.user)

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [RoleBasedAccess]

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [RoleBasedAccess]
