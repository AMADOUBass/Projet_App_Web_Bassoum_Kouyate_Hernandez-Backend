set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

# Create superuser if requested
if [[ $CREATE_SUPERUSER == "true" ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        '$DJANGO_SUPERUSER_USERNAME',
        '$DJANGO_SUPERUSER_EMAIL',
        '$DJANGO_SUPERUSER_PASSWORD'
    )
"
fi