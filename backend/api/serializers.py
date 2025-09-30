from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Player, SeasonStats, ReportAdmin , Participation, Event
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()

# ------------------------
# User Serializer
# ------------------------
class UserSerializer(serializers.ModelSerializer):
    is_player = serializers.ReadOnlyField()
    is_admin_user = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'password', 'role', 'phone_number', 'profile_picture',
            'bio', 'is_approved', 'is_player', 'is_admin_user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role', 'is_player', 'is_admin_user', 'is_approved']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ------------------------
# Register Serializer
# ------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_role(self, value):
        if value not in ['player', 'admin']:
            raise serializers.ValidationError("Rôle invalide.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        role = validated_data.get('role', 'player')
        username_base = email.split('@')[0]
        username = username_base
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{i}"
            i += 1

        if role == 'admin':
            user = User.objects.create_user(
                username=username,
                email=email,
                password=validated_data['password'],
                role='admin',
                is_active=True,
                is_approved=True,
                is_staff=True,
                is_superuser=True
            )
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=validated_data['password'],
                role='player',
                is_active=False,
                is_approved=False,
                is_staff=False,
                is_superuser=False
            )
        return user

# ------------------------
# JWT Token Serializer
# ------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Nettoyage email
        if isinstance(email, list):
            email = email[0]
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError("L'adresse e-mail n'est pas valide.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("L'utilisateur avec cet email n'existe pas.")

        if not user.check_password(password):
            raise serializers.ValidationError("Mot de passe incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("Le compte utilisateur n'est pas actif.")
        if not user.is_approved:
            if user.role == 'player':
                raise serializers.ValidationError("Ton compte joueur est en attente d'approbation par un administrateur.")
            elif user.role == 'admin':
                raise serializers.ValidationError("Ce compte administrateur n'est pas encore activé. Contacte le support.")
            else:
                raise serializers.ValidationError("Ce compte n'est pas encore approuvé.")

        # Génération des tokens
        refresh = self.get_token(user)
        access = refresh.access_token

        data = {
            'refresh': str(refresh),
            'access': str(access),
            'expires_in': access.lifetime.total_seconds(),
            'email': user.email,
            'role': user.role,
            'id': str(user.id),
        }

        return data

# ------------------------
# Player Serializer
# ------------------------

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = [
            'id', 'user', 'position',
            'jersey_number', 'is_available','created_at','updated_at'
        ]


# ------------------------
# Player Profile Serializer
# ------------------------

class PlayerProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    bio = serializers.CharField(source='user.bio', allow_blank=True, required=False)
    profile_picture = serializers.ImageField(source='user.profile_picture', allow_null=True, required=False)

    class Meta:
        model = Player
        fields = ['user', 'position', 'jersey_number', 'bio', 'profile_picture']


# ------------------------
# Unapproved User Serializer
# ------------------------

class UnapprovedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_approved']
        read_only_fields = ['id', 'email', 'username', 'role', 'is_approved']

# ------------------------
# SeasonStats Serializer
# ------------------------

class SeasonStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeasonStats
        fields = '__all__'

# ------------------------
# ReportAdmin Serializer
# ------------------------
class ReportAdminSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Vous devez être connecté pour accéder à cette ressource.")
        if not user.is_admin_user:
            raise serializers.ValidationError("Seuls les utilisateurs administrateurs peuvent créer des rapports.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Vous devez être connecté pour accéder à cette ressource.")
        if not user.is_admin_user:
            raise serializers.ValidationError("Seuls les utilisateurs administrateurs peuvent créer des rapports.")
        validated_data['created_by_admin'] = user
        return super().create(validated_data)

    class Meta:
        model = ReportAdmin
        fields = '__all__'
        read_only_fields = ['created_by_admin', 'created_at', 'updated_at']

# ------------------------
# Participation Serializer
# ------------------------
class ParticipationSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = Participation
        fields = [
            'id',
            'player',
            'player_name',
            'event',
            'event_title',
            'will_attend',
            'notified'
        ]

        read_only_fields = ['player', 'event', 'player_name', 'event_title']

    def get_player_name(self, obj):
        return obj.player.user.get_full_name() or obj.player.user.email

    def get_event_title(self, obj):
        return obj.event.title

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Vous devez être connecté pour accéder à cette ressource.")
        participation = self.instance

        # Si ce n’est pas l’admin et que ce n’est pas sa propre participation
        if participation and not user.is_admin_user and participation.player.user != user:
            raise serializers.ValidationError("Vous ne pouvez modifier que votre propre participation.")
        return data

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
