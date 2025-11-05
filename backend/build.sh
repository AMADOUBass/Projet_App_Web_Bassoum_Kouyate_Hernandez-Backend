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
bio = '$DJANGO_SUPERUSER_BIO'
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, telephone=telephone, bio=bio)
    print('Superuser created successfully.')
else:
    print('Superuser already exists, skipping creation.')
"
fi


# ✅ Temporarily show password
echo "Superuser email: $DJANGO_SUPERUSER_EMAIL"
echo "Superuser password: '$DJANGO_SUPERUSER_PASSWORD'"

# ⚡ Immediately delete/hide password from env
unset DJANGO_SUPERUSER_PASSWORD
echo "Password variable cleared for security."
