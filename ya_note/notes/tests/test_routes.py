from http import HTTPStatus

from django.urls import reverse
from notes.models import Note
from notes.tests.common import BaseTestCase


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

    def get_pages_detail_access(self):
        return (
            (
                self.author_client,
                reverse("notes:add"),
                HTTPStatus.OK,
            ),
            (
                self.author_client,
                reverse("notes:list"),
                HTTPStatus.OK,
            ),
            (
                self.author_client,
                reverse("notes:success"),
                HTTPStatus.OK,
            ),
            (
                self.author_client,
                reverse("notes:detail", args=(self.note.slug,)),
                HTTPStatus.OK,
            ),
            (
                self.author_client,
                reverse("notes:edit", args=(self.note.slug,)),
                HTTPStatus.OK,
            ),
            (
                self.author_client,
                reverse("notes:delete", args=(self.note.slug,)),
                HTTPStatus.OK,
            ),
            (
                self.reader_client,
                reverse("notes:detail", args=(self.note.slug,)),
                HTTPStatus.NOT_FOUND,
            ),
            (
                self.reader_client,
                reverse("notes:edit", args=(self.note.slug,)),
                HTTPStatus.NOT_FOUND,
            ),
            (
                self.reader_client,
                reverse("notes:delete", args=(self.note.slug,)),
                HTTPStatus.NOT_FOUND,
            ),
        )

    def get_not_user_pages(self):
        return (
            reverse("notes:add"),
            reverse("notes:list"),
            reverse("notes:success"),
            reverse("notes:detail", args=(self.note.slug,)),
            reverse("notes:edit", args=(self.note.slug,)),
            reverse("notes:delete", args=(self.note.slug,)),
        )

    def test_home_page(self):
        """Главная страница доступна для всех пользователей."""
        # Arrange - URL уже подготовлен
        url = reverse("notes:home")

        # Act
        response = self.client.get(url)

        # Assert
        assert response.status_code == HTTPStatus.OK

    def test_pages_status(self):
        """Страницы заметок доступны в зависимости от прав пользователя."""
        # Arrange - данные уже подготовлены в get_pages_detail_access

        # Act & Assert
        for client, url, expected_status in self.get_pages_detail_access():
            with self.subTest(
                    client=client,
                    url=url,
                    expected_status=expected_status,
            ):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                )

    def test_redirect_anonymous_user(self):
        """Анонимный пользователь перенаправляется на страницу входа."""
        # Arrange
        login_url = reverse("users:login")

        # Act & Assert
        for url in self.get_not_user_pages():
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f"{login_url}?next={url}"
                self.assertRedirects(response, redirect_url)

    def test_users_pages_available(self):
        """Страницы входа и регистрации доступны для всех пользователей."""
        # Arrange
        pages = (
            "users:login",
            "users:signup",
        )

        # Act & Assert
        for name in pages:
            with self.subTest(page=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available(self):
        """Страница выхода доступна для всех пользователей."""
        # Arrange
        url = reverse("users:logout")

        # Act
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.OK)
