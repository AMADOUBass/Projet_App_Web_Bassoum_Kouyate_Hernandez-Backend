# set -o errexit

# pip install -r requirements.txt

# python manage.py collectstatic --noinput

# python manage.py migrate

# # Create superuser if requested
# if [[ $CREATE_SUPERUSER == "true" ]]; then
#     python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
#     User.objects.create_superuser(
#         email='$DJANGO_SUPERUSER_EMAIL',
#         password='$DJANGO_SUPERUSER_PASSWORD'
#     )
# "
# fi
# echo "Superuser created with email: $DJANGO_SUPERUSER_EMAIL"
if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py createsuperuser \
    --noinput \
    --email "$DJANGO_SUPERUSER_EMAIL" \
    --username "$DJANGO_SUPERUSER_EMAIL" \
    || echo "Superuser already exists, skipping."
fi
