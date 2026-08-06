import pytest
from datetime import timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news(db):
    return News.objects.create(
        title="Заголовок",
        text="Текст",
    )


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username="Автор новости")


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username="Просто пользователь")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text="Текст")


@pytest.fixture
def news_list(db):
    today = timezone.now()
    return News.objects.bulk_create(
        [
            News(
                title=f"Заголовок {index}",
                text="Текст.",
                date=today - timedelta(days=index),
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    comments = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f"Текст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def comment_url(comment):
    return reverse("news:detail", args=(comment.news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse("news:delete", args=(comment.id,))


@pytest.fixture
def home():
    return reverse("news:home")


@pytest.fixture
def detail(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def logout():
    return reverse("users:logout")
