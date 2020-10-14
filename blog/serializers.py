from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Post, Tag
from drf_haystack.serializers import HaystackSerializerMixin
from rest_framework.serializers import CharField


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
        ]

class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = UserSerializer()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'created_time',
            'excerpt',
            'category',
            'author',
            'views',
        ]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
        ]

class PostRetrieveSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = UserSerializer()
    tags = TagSerializer(many=True)
    toc = serializers.CharField()
    body_html = serializers.CharField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'created_time',
            'excerpt',
            'category',
            'author',
            'views',
            'tags',
            'toc',
            'body_html',
        ]


# def get_serializer_class(self):
#     assert self.serializer_class is not None, (
#         "'%s' should either include a `serializer_class` attribute, "
#         "or override the `get_serializer_class()` method."
#         % self.__class__.__name__
#     )
#     return self.serializer_class


from .utils import Highlighter

class HighlightedCharField(CharField):
    def to_representation(self, value):
        value = super().to_representation(value)
        request = self.context["request"]
        query = request.query_params["text"]
        highlighter = Highlighter(query)
        return highlighter.highlight(value)

class PostHaystackSerializer(HaystackSerializerMixin, PostListSerializer):
    title = HighlightedCharField()
    summary = HighlightedCharField(source="body")

    class Meta(PostListSerializer.Meta):
        search_fields = ["text"]
        fields = [
            "id",
            "title",
            "summary",
            "created_time",
            "excerpt",
            "category",
            "author",
            "views",
        ]