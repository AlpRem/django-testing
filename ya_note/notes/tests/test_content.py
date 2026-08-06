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
        response = self.author_client.get(reverse("notes:list"))
        object_list = response.context["object_list"]
        self.assertEqual(
            object_list.count(),
            self.NOTES_COUNT_ON_LIST_PAGE
        )
        for note in self.author_notes:
            self.assertIn(note, object_list)
        for note in self.reader_notes:
            self.assertNotIn(note, object_list)

    def test_not_access_reader_notes(self):
        response = self.reader_client.get(reverse("notes:list"))
        object_list = response.context["object_list"]
        self.assertEqual(
            object_list.count(),
            self.NOTES_COUNT_ON_LIST_PAGE
        )
        for note in self.reader_notes:
            self.assertIn(note, object_list)
        for note in self.author_notes:
            self.assertNotIn(note, object_list)


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
        """Тест проверки наличия формы на редактирование и удаление"""
        pages = (
            reverse("notes:add"),
            reverse("notes:edit", args=(self.note.slug,)),
        )
        for url in pages:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn("form", response.context)
                self.assertIsInstance(
                    response.context["form"],
                    NoteForm,
                )
