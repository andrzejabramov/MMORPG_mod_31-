# posts/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Category, Post

User = get_user_model()


class PostsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='TK')

    def test_post_creation(self):
        """Тест создания поста"""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='Test Content',
            category=self.category
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
