#!/usr/bin/env bash
set -o errexit   # Stop script if any command fails

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser if requested
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'
telephone = '$DJANGO_SUPERUSER_TELEPHONE'
bio = '$DJANGO_SUPERUSER_BIO'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, telephone=telephone, bio=bio)
    print('Superuser created successfully.')
else:
    print('Superuser already exists, skipping creation.')
"
fi
# Insert demo players if CREATE_PLAYERS=true
if [[ "$CREATE_PLAYERS" == "true" ]]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
from players.models import Player
import uuid

User = get_user_model()

demo_players = [
  {'email': f'player{i}@club.com', 'first_name': f'Player{i}', 'last_name': 'Demo', 'phone_number': f'41800000{i}', 'position': 'Midfielder', 'jersey_number': i}
  for i in range(1, 11)
]

for data in demo_players:
  if not User.objects.filter(email=data['email']).exists():
    user = User.objects.create(
      id=uuid.uuid4(),
      email=data['email'],
      username=data['email'].split('@')[0],
      first_name=data['first_name'],
      last_name=data['last_name'],
      phone_number=data['phone_number'],
      role='player',
      is_approved=True
    )
    user.set_password('Defaultpass123##')
    user.save()
    Player.objects.create(
      user=user,
      position=data['position'],
      jersey_number=data['jersey_number'],
      is_available=True
    )
    print(f\"✅ Created player: {data['email']}\")
  else:
    print(f\"⚠️ Player already exists: {data['email']}\")
"
fi

# ✅ Temporarily show password
echo "Superuser email: $DJANGO_SUPERUSER_EMAIL"
echo "Superuser password: '$DJANGO_SUPERUSER_PASSWORD'"

# ⚡ Immediately delete/hide password from env
unset DJANGO_SUPERUSER_PASSWORD
echo "Password variable cleared for security."
