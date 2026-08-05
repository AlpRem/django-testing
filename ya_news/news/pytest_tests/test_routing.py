from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


def test_home_page(client, news):
    """Тест адресации домашний страницы"""
    url = reverse("news:home")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, news):
    """Тест адресации детализации новости"""
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ("client_fixture", "expected_status"),
    [
        ("author_client", HTTPStatus.OK),
        ("reader_client", HTTPStatus.NOT_FOUND),
    ],
)
@pytest.mark.parametrize(
    "name",
    [
        "news:edit",
        "news:delete",
    ],
)
def test_availability_for_comment_edit_and_delete(
    request,
    client_fixture,
    expected_status,
    name,
    comment,
):
    """Тест адресации удаления и редактирования комментария"""
    test_client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=(comment.id,))
    response = test_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name",
    [
        "news:edit",
        "news:delete",
    ],
)
def test_redirect_for_anonymous_client(
    client,
    comment,
    name,
):
    """Тест редеректа для анонимного пользователя"""
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.id,))
    redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    "name",
    [
        "users:login",
        "users:signup",
    ],
)
def test_auth_pages(client, name):
    """Тест адресации авторизации"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_page(client):
    """Тест адресации разлогирования"""
    url = reverse("users:logout")
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK
