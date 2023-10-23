from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

from rest_framework import serializers

from .models import Author, Category, Article, ArticleImage

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "date_joined", "last_login", "is_active"]


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "phone_number", "avatar", "user"]


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField(read_only=True)
    articles_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "heading", "slug", "articles_count"]

    def get_slug(self, category):
        return slugify(category.title)


class SimpleCategorySerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["title", "slug"]

    def get_slug(self, category):
        return slugify(category.title)


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ["id", "url"]

    def create(self, validated_data):
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)


class ArticleSerializer(serializers.ModelSerializer):
    category = SimpleCategorySerializer(read_only=True)
    slug = serializers.SerializerMethodField(read_only=True)
    images = ArticleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "category",
            "heading",
            "summary",
            "label",
            "slug",
            "created_at",
            "updated_at",
            "images",
        ]

    def get_slug(self, article):
        return slugify(article.heading)


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["category", "heading", "summary", "label"]
