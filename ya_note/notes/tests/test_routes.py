from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


class TestRoutes(TestCase):
    PAGES_ARGS = (
        'notes:add',
        'notes:list',
        'notes:success',
    )

    PAGES_SLUG = (
        'notes:detail',
        'notes:edit',
        'notes:delete',
    )

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Просто пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )

    def test_home_page(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_has_access(self):
        self.client.force_login(self.author)
        for name in self.PAGES_ARGS:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for name in self.PAGES_SLUG:
            with self.subTest(page=name):
                response = self.client.get(
                    reverse(name, args=(self.note.slug,))
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_unavailable_for_non_author(self):
        self.client.force_login(self.reader)
        for name in self.PAGES_SLUG:
            with self.subTest(page=name):
                response = self.client.get(
                    reverse(name, args=(self.note.slug,))
                )
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous_user(self):
        login_url = reverse('users:login')
        for name in self.PAGES_ARGS:
            with self.subTest(page=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in self.PAGES_SLUG:
            with self.subTest(page=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_users_pages_available(self):
        pages = (
            'users:login',
            'users:signup',
        )
        for name in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_available(self):
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
