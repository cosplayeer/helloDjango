from django.urls import path
 
from . import views

app_name = 'blog'
#参数1 URL 模式 ，参数2是视图函数
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    # path('posts/<int:pk>/', views.detail, name='detail'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    # path('archives/<int:year>/<int:month>/', views.archive, name='archive'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'),
    # 其他 url 配置
    # path('search/', views.search, name='search'),
    #最初级的首页api
    # path('api/index/', views.index),
    # GenericAPIView 类视图
    # path('api/index/', views.IndexPostListAPIView.as_view()),
    #视图集
    # path("api/index/",views.index)
]
