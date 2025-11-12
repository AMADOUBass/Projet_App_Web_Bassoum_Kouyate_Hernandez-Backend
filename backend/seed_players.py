import django
import os
import random
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # remplace par ton vrai nom de projet
django.setup()

from api.models import User, Player
from django.db import transaction

POSITIONS = ["Attaquant", "Milieu", "Défenseur", "Gardien"]
def create_seed_players(n=20):
    for i in range(n):
        email = f"joueur{i+1}@test.com"
        if User.objects.filter(email=email).exists():
            print(f"⚠️ Utilisateur déjà existant : {email}")
            continue

        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                password="test1234",
                is_approved=True,
                is_active=True,
            )
            Player.objects.create(
                user=user,
                team_name="FC Québec",
                position=random.choice(["Attaquant", "Milieu", "Défenseur", "Gardien"]),
                jersey_number=i + 1,
                is_available=True,
            )
            print(f"✅ Joueur créé : {email}")

    with transaction.atomic():
        for i in range(n):
            email = f"joueur{i+1}@test.com"
            password = "test1234"
            user = User.objects.create_user(
                email=email,
                password=password,
                is_approved=True,
                is_active=True,
            )
            player = Player.objects.create(
                user=user,
                team_name="FC Québec",
                position=random.choice(POSITIONS),
                jersey_number=i + 1,
                is_available=True,
            )
            print(f"✅ Joueur créé : {player.user.get_full_name()} ({player.position})")

if __name__ == "__main__":
    create_seed_players(20)