from http import HTTPStatus

from django.urls import reverse
from notes.models import Note
from notes.tests.common import BaseTestCase


class TestRoutes(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title="Заголовок", text="Текст", slug="slug", author=cls.author
        )

    def get_all_pages(self):
        return (
            reverse("notes:add"),
            reverse("notes:list"),
            reverse("notes:success"),
            reverse("notes:detail", args=(self.note.slug,)),
            reverse("notes:edit", args=(self.note.slug,)),
            reverse("notes:delete", args=(self.note.slug,)),
        )

    def get_private_pages(self):
        return (
            reverse("notes:detail", args=(self.note.slug,)),
            reverse("notes:edit", args=(self.note.slug,)),
            reverse("notes:delete", args=(self.note.slug,)),
        )

    def test_home_page(self):
        response = self.client.get(reverse("notes:home"))
        assert response.status_code == HTTPStatus.OK

    def test_authenticated_user_has_access(self):
        for url in self.get_all_pages():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                )

    def test_note_pages_unavailable_for_non_author(self):
        for url in self.get_private_pages():
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                )

    def test_redirect_anonymous_user(self):
        login_url = reverse("users:login")
        for url in self.get_all_pages():
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f"{login_url}?next={url}"
                self.assertRedirects(response, redirect_url)

    def test_users_pages_available(self):
        pages = (
            "users:login",
            "users:signup",
        )
        for name in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available(self):
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
