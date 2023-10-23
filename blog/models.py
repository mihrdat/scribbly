from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Author(BaseModel):
    phone_number = models.CharField(max_length=55, null=True, blank=True)
    avatar = models.ImageField(upload_to="blog/avatars", null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
