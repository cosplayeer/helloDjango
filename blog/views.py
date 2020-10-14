import re
import markdown
from django.shortcuts import render, get_object_or_404
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.views.generic import ListView, DetailView
from pure_pagination.mixins import PaginationMixin

from .models import Post, Category, Tag
from django.db.models import Q
#new rest
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Post
from .serializers import PostListSerializer, PostRetrieveSerializer
from comments.serializers import CommentSerializer

from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import AllowAny

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.serializers import DateField
from django_filters.rest_framework import DjangoFilterBackend
from .filters import PostFilter


class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 10

# def index(request):
#    post_list = Post.objects.all()
# #    post_list = Post.objects.all().order_by('-created_time')
#    return render(request, 'blog/index.html',context={'post_list': post_list})

# @api_view(http_method_names=["GET"])
# def index(request):
#     post_list = Post.objects.all().order_by('-created_time')
#     serializer = PostListSerializer(post_list, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# class IndexPostListAPIView(ListAPIView):
#     serializer_class = PostListSerializer
#     queryset = Post.objects.all()
#     pagination_class = LimitOffsetPagination  #PageNumberPagination
#     permission_classes = [AllowAny]

class PostViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
    ):
    serializer_class = PostListSerializer
    # ---if version
    # def get_serializer_class():
    #     if self.action == 'list':
    #         return PostListSerializer
    #     elif self.action == 'retrieve':
    #         return PostRetrieveSerializer
    #     else:
    #         return super().get_serializer_class()
    #--- attributes version
    serializer_class_table = {
        'list': PostListSerializer,
        'retrieve':PostRetrieveSerializer,
    }
    def get_serializer_class(self):
        return self.serializer_class_table.get(
             self.action, super().get_serializer_class()
        )
    queryset = Post.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]

    @action(
        methods=["GET"],
        detail=False,
        url_path="archive/dates",
        url_name="archive-date"
    )
    def list_archive_dates(self, request, *args, **kwargs):
        dates = Post.objects.dates('created_time', 'month', order='DESC')
        date_field = DateField()
        data = [date_field.to_representation(date) for date in dates]
        return Response(data=data, status=status.HTTP_200_OK)
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    
    @action(
        methods=["GET"],
        detail=True,
        url_path="comments",
        url_name="comment",
        pagination_class=LimitOffsetPagination,
        serializer_class=CommentSerializer,
    )
    def list_comments(self, request, *args, **kwargs):
        # 根据 URL 传入的参数值（文章 id）获取到博客文章记录
        post = self.get_object()
        # 获取文章下关联的全部评论
        queryset = post.comment_set.all().order_by("-created_time")
        # 对评论列表进行分页，根据 URL 传入的参数获取指定页的评论
        page = self.paginate_queryset(queryset)
        # 序列化评论
        serializer = self.get_serializer(page, many=True)
        # 返回分页后的评论列表
        return self.get_paginated_response(serializer.data)

class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    
    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super().get(request, *args, **kwargs)
        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()
        # 视图必须返回一个 HttpResponse 对象
        return response

    # def get_object(self, queryset=None):
    #     # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
    #     post = super().get_object(queryset=None)
    #     md = markdown.Markdown(extensions=[
    #     'markdown.extensions.extra',
    #     # 'markdown.extensions.codehilite',
    #     'markdown.extensions.fenced_code',
    #     # 'markdown.extensions.toc',
    #     TocExtension(slugify=slugify),
    #     ])
    #     post.body = md.convert(post.body)
    #     # print("post body: {}".format(post.body))
    #     # m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    #     # post.toc = m.group(1) if m is not None else ''
    #     return post

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 阅读量 +1
    post.increase_views()

    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        # 'markdown.extensions.codehilite',
        'markdown.extensions.fenced_code',
        # 'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    return render(request, 'blog/detail.html', context={'post': post})

class ArchiveView(IndexView):
    def get_queryset(self):
        # post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return (
        super(ArchiveView, self)
        .get_queryset()
        .filter(created_time__year=year,created_time__month=month)
        )

def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )  #.order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

class CategoryView(IndexView):
    # model = Post
    # template_name = 'blog/index.html'
    # context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)
    

def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate) #.order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

class TagView(IndexView):
    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=t)
    
def tag(request, pk):
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t) #.order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})    


def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = "请输入搜索关键词"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'post_list': post_list})


from drf_haystack.viewsets import HaystackViewSet
from .serializers import PostHaystackSerializer

class PostSearchView(HaystackViewSet):
    index_models = [Post]
    serializer_class = PostHaystackSerializer