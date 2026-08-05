from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = "Просто текст"

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="Автор заметки")
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse("notes:add")
        cls.form_data = {
            "title": "Заметка 1",
            "text": cls.NOTE_TEXT,
            "slug": "slug",
        }

    def test_anonymous_create(self):
        """Тест отсутствия возможности добавления заметки для неавторизованных пользователей"""
        response = self.client.post(
            self.url,
            data=self.form_data,
        )

        login_url = reverse("users:login")
        expected_url = f"{login_url}?next={self.url}"
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_user_create(self):
        """Тести добавления заметки для авторизованных пользователей"""
        response = self.auth_client.post(
            self.url,
            data=self.form_data,
        )
        self.assertRedirects(
            response,
            reverse("notes:success"),
        )
        notes_count = Note.objects.count()
        assert notes_count == 1
        note = Note.objects.get()
        assert note.title == "Заметка 1"
        assert note.text == self.NOTE_TEXT
        assert note.slug == "slug"
        assert note.author == self.user

    def test_duplicate_slug(self):
        """Тест отсутствия возможности добавления с уже существующим slug."""
        Note.objects.create(
            title="Заметка 1",
            text="Текст",
            slug="slug",
            author=self.user,
        )
        response = self.auth_client.post(
            self.url,
            data=self.form_data,
        )

        self.assertFormError(
            response.context["form"],
            "slug", errors="slug" + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Тест генерации slug при пустом slug"""
        form_data = self.form_data.copy()
        form_data.pop("slug")
        response = self.auth_client.post(
            self.url,
            data=form_data,
        )

        self.assertRedirects(response, reverse("notes:success"))
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(form_data["title"]))


class TestNoteEditDelete(TestCase):
    NEW_TITLE = "Заголовок 2"
    NEW_TEXT = "Текст 2"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор заметки")
        cls.reader = User.objects.create(username="Другой пользователь")

        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст",
            slug="test-slug",
            author=cls.author,
        )
        cls.edit_url = reverse(
            "notes:edit",
            args=(cls.note.slug,),
        )
        cls.delete_url = reverse(
            "notes:delete",
            args=(cls.note.slug,),
        )
        cls.form_data = {
            "title": cls.NEW_TITLE,
            "text": cls.NEW_TEXT,
            "slug": cls.note.slug,
        }

    def test_author_delete(self):
        """Тест удаления заметки автором"""
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(
            response,
            reverse("notes:success"),
        )
        self.assertEqual(
            Note.objects.count(),
            0,
        )

    def test_author_edi(self):
        """Тест редактирования заметки автором"""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertRedirects(
            response,
            reverse("notes:success"),
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.title,
            self.NEW_TITLE,
        )
        self.assertEqual(
            self.note.text,
            self.NEW_TEXT,
        )

    def test_user_delete(self):
        """Тест невозможности удаления заметки не автором"""
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(
            response.status_code,
            404,
        )
        self.assertEqual(
            Note.objects.count(),
            1,
        )

    def test_user_note(self):
        """Тест невозможности удаления заметки автором"""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertEqual(
            response.status_code,
            404,
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.title,
            "Заголовок",
        )
        self.assertEqual(
            self.note.text,
            "Текст",
        )
