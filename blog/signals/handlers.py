from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from blog.models import Author

User = get_user_model()


@receiver(post_save, sender=User)
def create_author_for_new_user(sender, **kwargs):
    if kwargs["created"]:
        Author.objects.create(user=kwargs["instance"])
