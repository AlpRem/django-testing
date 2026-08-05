from django.test import Client, TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_TITLE = "Заметка 1"
    NOTE_TEXT = "Просто текст"
    NOTE_SLUG = "slug"

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username="Автор заметки"
        )
        cls.reader = User.objects.create(
            username="Просто пользователь"
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
