#!/usr/bin/env bash
set -o errexit  # stop script if any command fails

# 1️⃣ Install dependencies
pip install -r requirements.txt

# 2️⃣ Collect static files
python manage.py collectstatic --noinput

# 3️⃣ Run migrations
python manage.py migrate

# 4️⃣ Create or update superuser
if [[ "$CREATE_SUPERUSER" == "true" ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'
# Check if superuser exists
try:
    u = User.objects.get(email=email)
    u.set_password(password)       # reset password if it exists
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Superuser exists: password updated')
except User.DoesNotExist:
    User.objects.create_superuser(email=email, password=password)
    print('Superuser created successfully')
"
fi

# 5️⃣ Log email & optional password
echo "Superuser email: $DJANGO_SUPERUSER_EMAIL"
echo "Superuser password (temporary, will be cleared): '$DJANGO_SUPERUSER_PASSWORD'"

# 6️⃣ Clear password from environment for security
unset DJANGO_SUPERUSER_PASSWORD
echo "Password variable cleared for security."

# 7️⃣ Start the app with Gunicorn + Uvicorn
python -m gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker
