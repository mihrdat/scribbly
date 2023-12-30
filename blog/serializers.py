from django.urls import reverse
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
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "username", "avatar"]

    def get_username(self, author):
        return author.user.username


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
        fields = [
            "id",
            "title",
            "heading",
            "slug",
            "articles_count",
            "parent",
            "children",
        ]
        read_only_fields = ["slug", "articles_count", "children"]

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
            "likes": article.likes_count,
            "comments": article.comments_count,
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

    def validate(self, data):
        article_id = self.context["article_id"]

        if ArticleLike.objects.filter(
            author=self.context["request"].user.author, article_id=article_id
        ).exists():
            raise serializers.ValidationError(
                {"author": "You have already liked this article."}
            )

        return super().validate(data)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)


class CommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "description", "reply_to"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        validated_data["parent_id"] = self.context["parent_id"]
        return super().create(validated_data)

    def validate_reply_to(self, value):
        if value is None:
            raise serializers.ValidationError("This field may not be null.")
        return value


class CommentReplySerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "description", "author", "reply_to"]

    def get_reply_to(self, comment):
        request = self.context.get("request")
        return {
            "username": comment.reply_to.user.username,
            "url": request.build_absolute_uri(
                reverse("author-detail", args=[comment.reply_to.id])
            ),
        }


class CommentSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)
    counts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "description", "author", "counts"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user.author
        validated_data["article_id"] = self.context["article_id"]
        return super().create(validated_data)

    def get_counts(self, comments):
        return {
            "replies": comments.replies_count,
        }
