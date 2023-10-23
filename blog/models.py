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


class Category(BaseModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    heading = models.CharField(max_length=255, null=True, blank=True)


class Article(BaseModel):
    heading = models.CharField(max_length=255, null=True, blank=True)
    summary = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=55, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="articles"
    )
