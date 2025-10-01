set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

# Create superuser if requested
if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py createsuperuser \
    --noinput \
    --email "$DJANGO_SUPERUSER_EMAIL" \
    --username "$DJANGO_SUPERUSER_EMAIL" \
    || echo "Superuser already exists, skipping."
fi
echo "Superuser created with email: $DJANGO_SUPERUSER_EMAIL"

