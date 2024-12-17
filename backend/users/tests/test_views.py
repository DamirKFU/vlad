import django.test
import django.urls
import parameterized
import rest_framework.status

import users.models


class AuthTestCase(django.test.TestCase):
    def setUp(self):
        self.register_url = django.urls.reverse("api:users:register")
        self.login_url = django.urls.reverse("api:users:login")
        self.test_user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
        )

    @parameterized.parameterized.expand(
        [
            (
                "valid_registration",
                {
                    "username": "testuser1",
                    "email": "test1@example.com",
                    "password": "TestPass123",
                },
                rest_framework.status.HTTP_201_CREATED,
                {
                    "status": "success",
                    "message": "Регистрация успешно завершена",
                },
            ),
            (
                "short_username",
                {
                    "username": "te",
                    "email": "test2@example.com",
                    "password": "TestPass123",
                },
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {
                        "username": [
                            "Имя пользователя должно быть от 5 до 32 символов."
                        ]
                    },
                    "message": "Ошибка при регистрации",
                },
            ),
            (
                "invalid_username_format",
                {
                    "username": "test@user",
                    "email": "test3@example.com",
                    "password": "TestPass123",
                },
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {
                        "username": [
                            "Имя пользователя может содержать только "
                            "латинские буквы, цифры и нижнее подчеркивание."
                        ]
                    },
                    "message": "Ошибка при регистрации",
                },
            ),
            (
                "invalid_email",
                {
                    "username": "testuser4",
                    "email": "invalid-email",
                    "password": "TestPass123",
                },
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {
                        "email": [
                            "Введите правильный адрес электронной почты."
                        ]
                    },
                    "message": "Ошибка при регистрации",
                },
            ),
            (
                "weak_password",
                {
                    "username": "testuser5",
                    "email": "test5@example.com",
                    "password": "password123",
                },
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {
                        "password": [
                            "Пароль должен содержать хотя "
                            "бы одну прописную букву."
                        ]
                    },
                    "message": "Ошибка при регистрации",
                },
            ),
        ]
    )
    def test_registration(
        self, name, payload, expected_status, expected_response
    ):
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.json(), expected_response)

    @parameterized.parameterized.expand(
        [
            (
                "valid_login",
                {"username": "testuser", "password": "TestPass123"},
                rest_framework.status.HTTP_200_OK,
                {"status": "success", "message": "Вход выполнен успешно"},
            ),
            (
                "wrong_password",
                {"username": "testuser", "password": "WrongPass123"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {"non_field_errors": ["Invalid credentials"]},
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "nonexistent_user",
                {"username": "nonexistent", "password": "TestPass123"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {"non_field_errors": ["Invalid credentials"]},
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "missing_password",
                {"username": "testuser"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {"password": ["Обязательное поле."]},
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "too_short_credentials",
                {"username": "test", "password": "short"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "status": "error",
                    "errors": {
                        "username": [
                            "Убедитесь, что это значение содержит "
                            "не менее 5 символов."
                        ],
                        "password": [
                            "Убедитесь, что это значение содержит "
                            "не менее 8 символов."
                        ],
                    },
                    "message": "Ошибка авторизации",
                },
            ),
        ]
    )
    def test_login(self, name, payload, expected_status, expected_response):
        response = self.client.post(self.login_url, payload)
        response_data = response.json()

        self.assertEqual(response.status_code, expected_status)

        self.assertEqual(response_data, expected_response)


class AuthTestCaseAdditional(django.test.TestCase):
    def setUp(self):
        self.register_url = django.urls.reverse("api:users:register")

    def test_duplicate_username_registration(self):
        first_user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "TestPass123",
        }
        self.client.post(self.register_url, first_user_data)

        second_user_data = {
            "username": "testuser",
            "email": "test2@example.com",
            "password": "TestPass123",
        }
        response = self.client.post(self.register_url, second_user_data)

        self.assertEqual(
            response.status_code, rest_framework.status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                "status": "error",
                "errors": {
                    "username": ["Пользователь с таким именем уже существует."]
                },
                "message": "Ошибка при регистрации",
            },
        )

    def test_duplicate_email_registration(self):
        first_user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "TestPass123",
        }
        self.client.post(self.register_url, first_user_data)

        second_user_data = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "TestPass123",
        }
        response = self.client.post(self.register_url, second_user_data)

        self.assertEqual(
            response.status_code, rest_framework.status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response.json(),
            {
                "status": "error",
                "errors": {
                    "email": ["Пользователь с таким email уже существует."]
                },
                "message": "Ошибка при регистрации",
            },
        )
