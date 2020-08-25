from .common import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost ', '.zmrenwu.com']
# ALLOWED_HOSTS = ['hellodjango-blog-tutorial-demo.zmrenwu.com']
# HAYSTACK_CONNECTIONS['default']['URL'] = 'http://hellodjango_blog_tutorial_elasticsearch:9200/'