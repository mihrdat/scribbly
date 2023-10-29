from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

from rest_framework import serializers

from .models import Author, Category, Article, ArticleImage, ArticleLike, Comment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "date_joined", "last_login", "is_active"]


class SimpleAuthorSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "email", "avatar"]

    def get_email(self, author):
        return author.user.email


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
        fields = ["id", "title", "heading", "slug", "articles_count", "parent"]

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
        fields = ["id", "image"]

    def create(self, validated_data):
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)


class ArticleSerializer(serializers.ModelSerializer):
    category = SimpleCategorySerializer(read_only=True)
    slug = serializers.SerializerMethodField(read_only=True)
    images = ArticleImageSerializer(many=True, read_only=True)
    counts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "category",
            "heading",
            "summary",
            "label",
            "slug",
            "images",
            "counts",
            "created_at",
            "updated_at",
        ]

    def get_slug(self, article):
        return slugify(article.heading)

    def get_counts(self, article):
        return {
            "likes_count": article.likes_count,
            "comments_count": article.comments_count,
        }


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["category", "heading", "summary", "label"]


class ArticleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleLike
        fields = ["id", "author"]
        read_only_fields = ["author"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)


class CommentReplySerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "description", "author", "reply_to"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        validated_data["parent_id"] = self.context["parent_id"]
        return super().create(validated_data)

    def validate_reply_to(self, value):
        if value is None:
            raise serializers.ValidationError("This field may not be null.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "description", "author", "replies_count"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)
