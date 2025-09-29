import re
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import PermissionDenied
from django.utils import timezone

# from .managers import UserManager
from .mixins import TimestampedModel

# -------------------------------
# Custom User Manager
# -------------------------------

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail doit être fournie")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("L'adresse e-mail fournie n'est pas valide")
        email = self.normalize_email(email)
        if not extra_fields.get("username"):
            extra_fields["username"] = email.split("@")[0]
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_approved", False)
        extra_fields.setdefault("role", "player")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("role", "admin")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
# -------------------------------
# Abstract Timestamped Model
# -------------------------------


# -------------------------------
# Custom User Model
# -------------------------------

class User(AbstractUser, TimestampedModel):
    """User model with roles: admin and player."""
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("player", "Player"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_player(self):
        return self.role == 'player'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def approve(self, admin_user):
        if not admin_user.is_admin_user:
            raise PermissionDenied("Seuls les administrateurs peuvent approuver les utilisateurs.")
        self.is_approved = True
        self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        if self.role == 'admin' and not (self.is_staff or self.is_superuser):
            raise ValueError("Seuls les utilisateurs avec les droits d'administrateur peuvent se voir attribuer le rôle d'administrateur.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']
        permissions = [
            ("can_approve_users", "Peut approuver les comptes utilisateurs"),
        ]

    def __str__(self):
        role_display = 'admin' if self.is_superuser else self.role
        return f"{self.email} ({role_display})"

# -------------------------------
# Player Model
# -------------------------------


class Player(TimestampedModel):
    """Player model representing a player in the system."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    team_name = models.CharField(max_length=100, default="FC Québec")
    position = models.CharField(max_length=30, blank=True)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.user.role != "player":
            raise ValueError("Le profil joueur ne peut être créé que pour les utilisateurs ayant le rôle 'player'.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        ordering = ['team_name', 'jersey_number', 'user__email']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"
    def summary(self):
        return f"Player {self.user.get_full_name() or self.user.email}, Team: {self.team}, Position: {self.position}, Jersey Number: {self.jersey_number}"


# -------------------------------
# Optional: PlayerProfile
# -------------------------------

class PlayerProfile(TimestampedModel):
    """Profile model for additional player information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile_details')
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in kg
    position = models.CharField(max_length=30, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name() or self.user.email}"

# -------------------------------
# Participation Model
# -------------------------------
class Participation(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    will_attend = models.BooleanField(default=False)  # Le joueur coche ce champ dans l'UI
    notified = models.BooleanField(default=False)     # Pour savoir si le joueur a été informé

    class Meta:
        verbose_name = 'Participation'
        verbose_name_plural = 'Participations'
        unique_together = ('player', 'event')
        ordering = ['event__date_event', 'player__user__email']

    def __str__(self):
        return f"{self.player.user.get_full_name() or self.player.user.email} - {self.event.title}"

# -------------------------------
# Event Model
# -------------------------------

class Event(TimestampedModel):
    EVENT_TYPES = [
        ('Entrainement', 'Entrainement'),
        ('Match', 'Match'),
        ('Tournoi', 'Tournoi'),
        ('Amical', 'Amical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date_event = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    opponent = models.JSONField(default=dict, blank=True) 
    is_cancelled = models.BooleanField(default=False)
    participants = models.ManyToManyField('Player', through='Participation', related_name='events', blank=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date_event']
        permissions = [
            ("can_manage_events", "Can create, update, delete events"),
        ]
    def save (self, *args, **kwargs):
        if self.event_type in ['Match', 'Tournoi', 'Amical'] and not self.opponent:
            raise ValueError("Les événements de type Match, Tournoi ou Amical doivent avoir un adversaire.")
        if self.date_event and self.date_event < timezone.now():
            raise ValueError("La date de l'événement ne peut pas être dans le passé.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.event_type})"

# -------------------------------
# ReportAdmin Model
# -------------------------------
class ReportAdmin(TimestampedModel):
    REPORT_TYPES = [
        ('match', 'Rapport de match'),
        ('global', 'Rapport global'),
        ('evaluation', 'Rapport d\'évaluation'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    reporter_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    content = models.TextField()
    created_by_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_made')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.created_by_admin and not self.created_by_admin.is_admin_user:
            raise PermissionError("Seuls les admins peuvent créer des rapports.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Report Admin'
        verbose_name_plural = 'Reports Admin'
        ordering = ['-created_at']

    def __str__(self):
        reporter_email = self.created_by_admin.email if self.created_by_admin else "Unknown"
        return f"{self.title} ({self.reporter_type}) by {reporter_email}"
    
# -------------------------------
# SeasonStats Model
# -------------------------------
class SeasonStats(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='season_stats')
    season_year = models.CharField(max_length=9)  # e.g., "2025-2026"
    games_played = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)
    notes_moyenne_saison = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('player', 'season_year')
        ordering = ['-season_year', 'player__user__email']

    def __str__(self):
        return f"{self.player.user.get_full_name() or self.player.user.email} - Saison {self.season_year}"