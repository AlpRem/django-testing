import pytest
from django.conf import settings
from news.forms import CommentForm


@pytest.mark.usefixtures("news_list")
def test_news_count(client, home):
    """Тест проверки количества новостей"""
    response = client.get(home)
    object_list = response.context["object_list"]
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures("news_list")
def test_news_order(client, home):
    """Тест проверки сортировки новостей"""
    response = client.get(home)
    object_list = response.context["object_list"]
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.usefixtures("comments")
def test_comments_order(client, news, detail):
    """Тест проверки сортировки комантарий новости"""
    response = client.get(detail)
    news_object = response.context["news"]
    all_comments = news_object.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news, detail):
    """Тест проверки отсутствия передачи формы для анонимного пользователя"""
    response = client.get(detail)
    assert "form" not in response.context


def test_authorized_client_has_form(client, news, author, detail):
    """Тест проверки передачи формы для авторизованного пользователя"""
    client.force_login(author)
    response = client.get(detail)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
