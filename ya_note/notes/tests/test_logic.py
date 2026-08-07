from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from notes.tests.common import BaseTestCase
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(BaseTestCase):
    NOTE_TEXT = "Просто текст"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("notes:add")
        cls.form_data = {
            "title": cls.NOTE_TITLE,
            "text": cls.NOTE_TEXT,
            "slug": cls.NOTE_SLUG,
        }

    def test_anonymous_create(self):
        """Неавторизованный пользователь не может создать заметку."""
        login_url = reverse("users:login")
        expected_url = f"{login_url}?next={self.url}"

        # Act
        response = self.client.post(
            self.url,
            data=self.form_data,
        )

        # Assert
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_user_create(self):
        """Авторизованный пользователь может создать заметку."""
        # Arrange - данные уже подготовлены в setUpTestData
        success_url = reverse("notes:success")

        # Act
        response = self.author_client.post(
            self.url,
            data=self.form_data,
        )

        # Assert
        self.assertRedirects(response, success_url)
        notes_count = Note.objects.count()
        assert notes_count == 1
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_duplicate_slug(self):
        """Заметка с уже существующим slug не создается."""
        # Arrange
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.author,
        )

        # Act
        response = self.author_client.post(
            self.url,
            data=self.form_data,
        )

        # Assert
        self.assertFormError(
            response.context["form"],
            "slug",
            errors=f"slug{WARNING}",
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """При пустом slug генерируется автоматически."""
        # Arrange
        form_data = self.form_data.copy()
        form_data.pop("slug")
        success_url = reverse("notes:success")

        # Act
        response = self.author_client.post(
            self.url,
            data=form_data,
        )

        # Assert
        self.assertRedirects(response, success_url)
        note = Note.objects.get()
        self.assertEqual(note.slug, slugify(form_data["title"]))


class TestNoteEditDelete(BaseTestCase):
    NEW_TITLE = "Заголовок 2"
    NEW_TEXT = "Текст 2"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
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
        """Автор может удалить свою заметку."""
        # Arrange - данные уже подготовлены в setUpTestData
        success_url = reverse("notes:success")

        # Act
        response = self.author_client.post(self.delete_url)

        # Assert
        self.assertRedirects(response, success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_author_edit(self):
        """Автор может редактировать свою заметку."""
        # Arrange - данные уже подготовлены в setUpTestData
        success_url = reverse("notes:success")

        # Act
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )

        # Assert
        self.assertRedirects(response, success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_delete(self):
        """Пользователь не может удалить чужую заметку."""
        # Arrange - данные уже подготовлены в setUpTestData

        # Act
        response = self.reader_client.post(self.delete_url)

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_note(self):
        """Пользователь не может редактировать чужую заметку."""
        # Arrange - данные уже подготовлены в setUpTestData

        # Act
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )

        # Assert
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
