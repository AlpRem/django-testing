import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


HOME_URL = reverse("news:home")


@pytest.mark.usefixtures("news_list")
def test_news_count(client):
    """Количество новостей на главной не превышает лимит."""
    response = client.get(HOME_URL)
    object_list = response.context["object_list"]
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures("news_list")
def test_news_order(client):
    """Новости на главной сортируются от новых к старым."""
    response = client.get(HOME_URL)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.usefixtures("comments")
def test_comments_order(client, news, detail):
    """Комментарии к новости сортируются от новых к старым."""
    response = client.get(detail)
    news_object = response.context["news"]
    all_comments = news_object.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news, detail):
    """Анонимный пользователь не видит форму комментария."""
    response = client.get(detail)
    assert "form" not in response.context


def test_authorized_client_has_form(client, news, author, detail):
    """Авторизованный пользователь видит форму комментария."""
    client.force_login(author)
    response = client.get(detail)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
