# responses/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Category, Post
from responses.models import Response

User = get_user_model()


class ResponsesTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='pass123'
        )
        self.responder = User.objects.create_user(
            username='responder',
            email='responder@example.com',
            password='pass123'
        )
        self.category = Category.objects.create(name='TK')
        self.post = Post.objects.create(
            author=self.author,
            title='Test Post',
            content='Test Content',
            category=self.category
        )

    def test_response_creation(self):
        """Тест создания отклика"""
        response = Response.objects.create(
            post=self.post,
            author=self.responder,
            text='Test Response'
        )
        self.assertEqual(response.text, 'Test Response')
        self.assertEqual(response.author, self.responder)
        self.assertFalse(response.is_accepted)
