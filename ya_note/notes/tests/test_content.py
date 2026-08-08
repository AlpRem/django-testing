from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.common import BaseTestCase


class TestNoteList(BaseTestCase):
    NOTES_COUNT_ON_LIST_PAGE = 10

    @classmethod
    def create_notes(cls, author):
        Note.objects.bulk_create(
            [
                Note(
                    title=f"{cls.NOTE_TITLE} {index}",
                    text=cls.NOTE_TEXT,
                    slug=f"{cls.NOTE_SLUG}-{author.pk}-{index}",
                    author=author,
                )
                for index in range(cls.NOTES_COUNT_ON_LIST_PAGE)
            ]
        )
        return list(Note.objects.filter(author=author))

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.author_notes = cls.create_notes(cls.author)
        cls.reader_notes = cls.create_notes(cls.reader)

    def test_access_author_notes(self):
        """Автор видит только свои заметки на странице списка."""
        # Arrange
        url = reverse("notes:list")

        # Act
        response = self.author_client.get(url)

        # Assert
        self.assertQuerySetEqual(
            response.context["object_list"].order_by("pk"),
            self.author_notes,
            ordered=True,
        )

    def test_not_access_reader_notes(self):
        """Читатель видит только свои заметки на странице списка."""
        # Arrange
        url = reverse("notes:list")

        # Act
        response = self.reader_client.get(url)

        # Assert
        self.assertQuerySetEqual(
            response.context["object_list"].order_by("pk"),
            self.reader_notes,
            ordered=True,
        )


class TestNotePages(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )

    def test_pages_have_form(self):
        """Форма для создания и редактирования заметки доступна автору."""
        # Arrange
        pages = (
            reverse("notes:add"),
            reverse("notes:edit", args=(self.note.slug,)),
        )

        # Act & Assert
        for url in pages:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(
                    response.context["form"],
                    NoteForm,
                )
