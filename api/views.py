import re
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated
from .models import User, Player, SeasonStats, Participation, ReportAdmin, Event
from .permissions import RoleBasedAccess
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
    EventSerializer,
    ApprovedUserSerializer,
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
# List of Unapproved Users (admin only)
# ------------------------
class ApprovedUserListView(generics.ListAPIView):
    serializer_class = ApprovedUserSerializer
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def get_queryset(self):
        return User.objects.filter(is_approved=True).exclude(role='admin')

# ------------------------
# Approve a User (admin only)
# ------------------------
class ApproveUserView(APIView):
    permission_classes = [RoleBasedAccess]
    admin_only = True

    def post(self, request, user_id):
        user_to_approve = get_object_or_404(User, id=user_id)
        if user_to_approve.is_active:
            return Response({"detail": "L'utilisateur est déjà actif."}, status=status.HTTP_400_BAD_REQUEST)
        if user_to_approve.is_approved:
            return Response({"detail": "L'utilisateur est déjà approuvé."}, status=status.HTTP_400_BAD_REQUEST)
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
        # ✅ On filtre par joueur connecté et on optimise les relations
        return (
            Participation.objects
            .select_related("event", "player__user")  # charge l'événement et le joueur
            .filter(player__user=user)
            .order_by("-event__date_event")  # les plus récents d'abord
        )

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.filter(is_cancelled=False,date_event__gte=timezone.now())
    serializer_class = EventSerializer
    permission_classes = [RoleBasedAccess]

class EventRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [RoleBasedAccess]


# ------------------------
# Validation ajax
# ------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_email(request):
    email = request.data.get("email", "").strip().lower()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"

    if not email:
        return Response({"error": "L'email est requis."}, status=400)

    if not re.fullmatch(pattern, email):
        return Response({"error": "Format d'email invalide."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Cet email est déjà utilisé."}, status=409)

    return Response({"success": "L'email est disponible."}, status=200)


# validate password strength
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_password(request):
    password = request.data.get("password", "")

    if not password.strip():
        return Response({"valid": False, "error": "Le mot de passe est requis."}, status=400)

    rules = [
        (len(password) >= 8, "Le mot de passe doit contenir au moins 8 caractères."),
        (re.search(r"[A-Z]", password), "Il doit contenir au moins une lettre majuscule."),
        (re.search(r"[a-z]", password), "Il doit contenir au moins une lettre minuscule."),
        (re.search(r"[0-9]", password), "Il doit contenir au moins un chiffre."),
        (re.search(r"[^\w\s]", password), "Il doit contenir au moins un caractère spécial."),
    ]

    for valid, message in rules:
        if not valid:
            return Response({"valid":False,"error": message}, status=400)

    return Response({"valid": True, "success": "Mot de passe sécurisé."}, status=200)


#validate login
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_login(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response({"error": "Email et mot de passe sont requis."}, status=400)

    try:
        user = User.objects.get(email=email)

        if not user.check_password(password):
            return Response({"error": "Les identifiants sont invalides."}, status=401)

        if not user.is_active or not user.is_approved:
            return Response({"error": "Le compte n'est pas actif ou approuvé."}, status=403)

        return Response({"success": "Connexion réussie."}, status=200)

    except User.DoesNotExist:
        return Response({"error": "Les identifiants sont invalides."}, status=401)