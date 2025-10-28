from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User,Player

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un Player après la création d'un User"""
    if created and instance.role == "player":
        Player.objects.create(user=instance)
