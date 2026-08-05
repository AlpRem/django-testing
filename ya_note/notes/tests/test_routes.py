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
        response = self.client.get(reverse("notes:home"))
        assert response.status_code == HTTPStatus.OK

    def test_pages_status(self):
        for client, url, expected_status in self.get_pages_detail_access():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    response.status_code,
                    expected_status,
                )

    def test_redirect_anonymous_user(self):
        login_url = reverse("users:login")
        for url in self.get_not_user_pages():
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
