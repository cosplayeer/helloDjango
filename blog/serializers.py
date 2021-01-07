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
    # 不能在Meta.fields直接添加
    #     对于这里提到的 toc、body_html 属性，django-rest-framework 就无法推断其值的类型，也就无法自动使用对应的序列化字段对其进行序列化了。不过解决方法很简单，既然 django-rest-framework 无法自动推断，那我们就人工指定该使用何种类型的序列化字段就行了。
    # 这里需要序列化的字段值都是字符串，因此在序列化器中显示地指定需要序列化的字段以及使用的系列化字段类型就可以了
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