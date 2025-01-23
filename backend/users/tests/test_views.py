import django.test
import django.urls
import parameterized
import rest_framework.status
import rest_framework.test

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

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

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
                    "data": {},
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
                    "errors": {
                        "fields": {
                            "username": (
                                "Имя пользователя должно быть от 5 до 32 "
                                "символов."
                            )
                        },
                        "form_error": None,
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
                    "errors": {
                        "fields": {
                            "username": (
                                "Имя пользователя может содержать только "
                                "латинские буквы, цифры и нижнее "
                                "подчеркивание."
                            )
                        },
                        "form_error": None,
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
                    "errors": {
                        "fields": {
                            "email": (
                                "Введите правильный адрес электронной почты."
                            )
                        },
                        "form_error": None,
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
                    "errors": {
                        "fields": {
                            "password": (
                                "Пароль должен содержать хотя "
                                "бы одну прописную букву."
                            )
                        },
                        "form_error": None,
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
                {"data": {}, "message": "Вход выполнен успешно"},
            ),
            (
                "wrong_password",
                {"username": "testuser", "password": "WrongPass123"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "errors": {
                        "fields": {},
                        "form_error": "Пользователь не найден",
                    },
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "nonexistent_user",
                {"username": "nonexistent", "password": "TestPass123"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "errors": {
                        "fields": {},
                        "form_error": "Пользователь не найден",
                    },
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "missing_password",
                {"username": "testuser"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "errors": {
                        "fields": {"password": "Обязательное поле."},
                        "form_error": None,
                    },
                    "message": "Ошибка авторизации",
                },
            ),
            (
                "too_short_credentials",
                {"username": "test", "password": "short"},
                rest_framework.status.HTTP_400_BAD_REQUEST,
                {
                    "errors": {
                        "fields": {
                            "username": (
                                "Убедитесь, что это значение содержит "
                                "не менее 5 символов."
                            ),
                            "password": (
                                "Убедитесь, что это значение содержит "
                                "не менее 8 символов."
                            ),
                        },
                        "form_error": None,
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

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

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
                "errors": {
                    "fields": {
                        "username": (
                            "Пользователь с таким именем уже существует."
                        )
                    },
                    "form_error": None,
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
                "errors": {
                    "fields": {
                        "email": "Пользователь с таким email уже существует."
                    },
                    "form_error": None,
                },
                "message": "Ошибка при регистрации",
            },
        )


@django.test.override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class PasswordResetTestCase(django.test.TestCase):
    def setUp(self):
        self.user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="OldPass123",
        )

        self.reset_request_url = django.urls.reverse(
            "api:users:password_reset_request"
        )
        self.reset_confirm_url = django.urls.reverse(
            "api:users:password_reset_confirm"
        )

    def tearDown(self):
        django.core.mail.outbox = []
        users.models.User.objects.all().delete()
        super().tearDown()

    def test_password_reset_request_valid_email(self):
        response = self.client.post(
            self.reset_request_url, {"email": "test@example.com"}
        )

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_200_OK,
            "Неверный код ответа при успешном запросе сброса пароля",
        )
        self.assertEqual(
            response.json(),
            {
                "data": {},
                "message": (
                    "Инструкции по сбросу пароля отправлены на вашу почту"
                ),
            },
            "Неверный формат ответа при успешном запросе сброса пароля",
        )
        self.assertEqual(len(django.core.mail.outbox), 1)
        self.assertEqual(django.core.mail.outbox[0].subject, "Сброс пароля")
        self.assertEqual(django.core.mail.outbox[0].to, ["test@example.com"])

    def test_password_reset_request_invalid_email(self):
        response = self.client.post(
            self.reset_request_url, {"email": "nonexistent@example.com"}
        )

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_400_BAD_REQUEST,
            "Неверный код ответа при неверном email",
        )

        self.assertEqual(
            response.json(),
            {
                "errors": {
                    "fields": {},
                    "form_error": "Пользователь с таким email не найден.",
                },
                "message": "Ошибка при запросе сброса пароля",
            },
            "Неверный формат ответа при неверном email",
        )
        self.assertEqual(len(django.core.mail.outbox), 0)

    def test_password_reset_confirm_valid_token(self):
        self.client.post(self.reset_request_url, {"email": "test@example.com"})

        email_content = django.core.mail.outbox[0].alternatives[0][0]
        token_start = email_content.find("/reset-password/") + len(
            "/reset-password/"
        )
        token_end = email_content.find('"', token_start)
        token = email_content[token_start:token_end]
        new_password = "NewPass123"

        response = self.client.post(
            self.reset_confirm_url, {"token": token, "password": new_password}
        )

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_200_OK,
            "Неверный код ответа при успешном сбросе пароля",
        )
        self.assertEqual(
            response.json(),
            {"data": {}, "message": "Пароль успешно изменен."},
            "Неверный формат ответа при успешном сбросе пароля",
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_confirm_invalid_token(self):
        response = self.client.post(
            self.reset_confirm_url,
            {"token": "invalid-token", "password": "NewPass123"},
        )

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_400_BAD_REQUEST,
            "Неверный код ответа при неверном токене",
        )
        self.assertEqual(
            response.json(),
            {
                "errors": {
                    "fields": {
                        "token": (
                            "Недействительная или "
                            "просроченная ссылка для сброса пароля."
                        )
                    },
                    "form_error": None,
                },
                "message": "Ошибка при сбросе пароля",
            },
            "Неверный формат ответа при неверном токене",
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPass123"))


class LogoutViewTest(django.test.TestCase):
    def setUp(self):
        self.user = users.models.User.objects.create_user(
            username="testuser",
            password="TestPass123",
        )
        self.client = rest_framework.test.APIClient()
        self.logout_url = django.urls.reverse("api:users:logout")

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

    def test_logout_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_200_OK,
            "Неверный код ответа при успешном выходе",
        )
        self.assertEqual(
            response.json(),
            {"data": {}, "message": "Выход выполнен успешно"},
            "Неверный формат ответа при успешном выходе",
        )

    def test_logout_unauthorized(self):
        response = self.client.post(self.logout_url)

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_401_UNAUTHORIZED,
            "Неверный код ответа для неавторизованного пользователя",
        )


class IsAuthViewTest(django.test.TestCase):
    def setUp(self):
        self.user = users.models.User.objects.create_user(
            username="testuser",
            password="TestPass123",
        )
        self.client = rest_framework.test.APIClient()
        self.is_auth_url = django.urls.reverse("api:users:is_auth")

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

    def test_is_auth_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.is_auth_url)

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_200_OK,
            "Неверный код ответа для авторизованного пользователя",
        )
        self.assertEqual(
            response.json(),
            {"data": {}, "message": "Вы авторизованы"},
            "Неверный формат ответа для авторизованного пользователя",
        )

    def test_is_auth_unauthorized(self):
        response = self.client.post(self.is_auth_url)

        self.assertEqual(
            response.status_code,
            rest_framework.status.HTTP_401_UNAUTHORIZED,
            "Неверный код ответа для неавторизованного пользователя",
        )
