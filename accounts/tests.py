# accounts/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import OneTimeCode

User = get_user_model()


class AccountsTestCase(TestCase):
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_one_time_code_generation(self):
        """Тест генерации кода"""
        code = OneTimeCode.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())


from django.test import TestCase

# Create your tests here.
