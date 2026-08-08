from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.pytest_tests.urls import HOME_URL, LOGOUT_URL


def test_home_pages(client, news):
    """Главная страница доступна анонимному пользователю."""
    # Act
    response = client.get(HOME_URL)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_detail_pages(client, detail):
    """Страница новости доступна анонимному пользователю."""
    response = client.get(detail)

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
    """Редактирование и удаление комментария доступны только автору."""
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
    """Анонимный пользователь перенаправляется на страницу входа."""
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
    """Страницы входа и регистрации доступны для всех пользователей."""
    url = reverse(name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_logout_page(client):
    """Страница выхода доступна для всех пользователей."""
    response = client.post(LOGOUT_URL)

    assert response.status_code == HTTPStatus.OK
