from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

class TestNoteList(TestCase):
    NOTES_COUNT_ON_LIST_PAGE = 10

    @classmethod
    def create_notes(cls, author):
        return Note.objects.bulk_create(
            [
                Note(
                    title=f'Заметка {index}',
                    text='Просто текст.',
                    slug=f'slug-{author.pk}-{index}',
                    author=author,
                )
                for index in range(cls.NOTES_COUNT_ON_LIST_PAGE)
            ]
        )

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Просто пользователь')
        cls.author_notes = cls.create_notes(cls.author)
        cls.reader_notes = cls.create_notes(cls.reader)

    def test_notes_access(self):
        users_notes = (
            (self.author, self.author_notes, self.reader_notes),
            (self.reader, self.reader_notes, self.author_notes),
        )
        for user, visible_notes, hidden_notes in users_notes:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertEqual(
                    object_list.count(),
                    self.NOTES_COUNT_ON_LIST_PAGE
                )
                for note in visible_notes:
                    self.assertIn(note, object_list)
                for note in hidden_notes:
                    self.assertNotIn(note, object_list)


class TestNotePages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

    def test_pages_have_form(self):
        self.client.force_login(self.author)
        pages = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                )