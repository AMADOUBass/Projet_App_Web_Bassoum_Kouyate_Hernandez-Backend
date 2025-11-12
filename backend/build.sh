#!/usr/bin/env bash
set -o errexit   # Stop script if any command fails

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# 🔐 Create superuser if requested
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'
bio = '$DJANGO_SUPERUSER_BIO'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, bio=bio)
    print('✅ Superuser created successfully.')
else:
    print('⚠️ Superuser already exists, skipping creation.')
"
fi

# ⚽ Créer 10 joueurs avec stats pour 2025 si demandé
if [[ "$CREATE_FAKE_PLAYERS" == "true" ]]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
from api.models import Player
from api.models import SeasonStats
import random
from decimal import Decimal

User = get_user_model()

positions = [
    'Gardien', 'Défenseur central', 'Latéral gauche', 'Latéral droit',
    'Milieu défensif', 'Milieu central', 'Milieu offensif',
    'Ailier gauche', 'Ailier droit', 'Attaquant'
]

for i in range(1, 11):
    email = f'joueur{i}@test.com'
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(
            email=email,
            password='Testpass123##',
            first_name=f'Joueur{i}'
        )
        position = random.choice(positions)
        player, created = Player.objects.get_or_create(user=user, defaults={'position': position})
        if created:
            print(f'Joueur {i} créé avec profil Player')
        else:
            print(f'Joueur {i} a déjà un profil Player')

        SeasonStats.objects.create(
            player=player,
            season_year=2025,
            games_played=random.randint(5, 20),
            goals=random.randint(0, 10),
            assists=random.randint(0, 8),
            yellow_cards=random.randint(0, 4),
            red_cards=random.randint(0, 2),
            notes_moyenne_saison=Decimal(str(round(random.uniform(5.5, 8.5), 2)))
        )
        print(f'Joueur {i} créé avec stats ({position})')
    else:
        print(f'Joueur {i} déjà existant')
  "
fi

# ✅ Temporarily show password
echo "Superuser email: $DJANGO_SUPERUSER_EMAIL"
echo "Superuser password: '$DJANGO_SUPERUSER_PASSWORD'"

# ⚡ Immediately delete/hide password from env
unset DJANGO_SUPERUSER_PASSWORD
echo "Password variable cleared for security."
