from datetime import timedelta

from django.apps import apps
from django.contrib.auth.models import User
from django.template import Context, Template
from django.utils import timezone

from blog.models import Category, Post
from .base import CommentDataTestCase
from ..forms import CommentForm
from ..models import Comment
from ..templatetags.comments_extras import show_comment_form, show_comments


class CommentExtraTestCase(CommentDataTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ctx = Context()
        #...省略其它测试用例的代码

    def test_show_comment_form_with_invalid_bound_form(self):
        template = Template(
            '{% load comments_extras %}'
            '{% show_comment_form post form %}'
        )
        invalid_data = {
            'email': 'invalid_email',
        }
        form = CommentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        context = Context(show_comment_form(self.ctx, self.post, form=form))
        expected_html = template.render(context)

        for field in form:
            label = '<label for="{}">{}：</label>'.format(field.id_for_label, field.label)
            self.assertInHTML(label, expected_html)
            self.assertInHTML(str(field), expected_html)
            self.assertInHTML(str(field.errors), expected_html)