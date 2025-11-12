from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    # Auth
    RegisterView, CurrentUserView, CustomTokenObtainPairView,

    # Admin
    UnapprovedUserListView, ApproveUserView,ApprovedUserListView,
    SeasonStatsAdminListView, SeasonStatsDetailView,
    EventParticipationView, ReportAdminCreateView, ReportAdminListView,

    # Player
    PlayerProfileView, PlayerParticipationUpdateView, MyParticipationsView,
    MySeasonStatsView, PlayerViewSet, UserUpdateView,

    # Ajax Validation
    validate_password, validate_login, validate_email,

    #Event
    EventListCreateView, EventRetrieveUpdateDestroyView,

    #Participation
    GiveNotesToPlayerCreateView,
)
router = DefaultRouter()
router.register(r'admin/players', PlayerViewSet, basename='player')

urlpatterns = [
    # ------------------------
    # 🔐 Authentification
    # ------------------------
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/current-user/', CurrentUserView.as_view(), name='current_user'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ------------------------
    # 🛡 Admin-only routes
    # ------------------------
    path('admin/users/<uuid:pk>/', UserUpdateView.as_view(), name='user_update'),
    path('admin/unapproved-users/', UnapprovedUserListView.as_view(), name='unapproved_users'),
    path('admin/approved-users/', ApprovedUserListView.as_view(), name='approved_users'),
    path('admin/approve-player/<uuid:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    # path('admin/players/', PlayerListView.as_view(), name='player_list'),
    path('admin/season-stats/', SeasonStatsAdminListView.as_view(), name='admin_season_stats'),
    path('admin/season-stats/<uuid:pk>/', SeasonStatsDetailView.as_view(), name='season_stats_detail'),
    path('admin/event/<uuid:event_id>/participations/', EventParticipationView.as_view(), name='event_participations'),
    path('admin/reports/', ReportAdminListView.as_view(), name='report_admin_list'),
    path('admin/reports/create/', ReportAdminCreateView.as_view(), name='report_admin_create'),

    # ------------------------
    # ⚽ Player-only routes
    # ------------------------
    path('player/profile/', PlayerProfileView.as_view(), name='player_profile'),
    path('player/participation/<uuid:pk>/', PlayerParticipationUpdateView.as_view(), name='player_participation_update'),
    path('player/my-participations/', MyParticipationsView.as_view(), name='my_participations'),
    path('player/my-season-stats/', MySeasonStatsView.as_view(), name='my_season_stats'),

    # ------------------------
    # 🧪 Validation Ajax routes
    # ------------------------
    path("auth/validate-password/", validate_password, name="validate_password"),
    path("auth/validate-login/", validate_login, name="validate_login"),
    path("auth/validate-email/", validate_email, name="validate_email"),

    # ------------------------
    # 📅 Events routes
    # ------------------------
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<uuid:pk>/', EventRetrieveUpdateDestroyView.as_view(), name='event-detail'),

    # ------------------------
    # 📅 Participations routes
    # ------------------------
    path('give-notes-to-player/',GiveNotesToPlayerCreateView.as_view(), name='give-notes-to-player'),

] + router.urls
