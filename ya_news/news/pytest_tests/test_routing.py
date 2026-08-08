from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.pytest_tests.urls import HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL


@pytest.mark.parametrize(
    "url",
    [
        HOME_URL,
        LOGIN_URL,
        SIGNUP_URL
    ],
)
def test_public_pages(client, news, url):
    """Главная страница и страницы авторизации доступны всем."""
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, detail):
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
    url = reverse(name, args=(comment.id,))
    redirect_url = f"{LOGIN_URL}?next={url}"

    response = client.get(url)

    assertRedirects(response, redirect_url)


def test_logout_page(client):
    """Страница выхода доступна для всех пользователей."""
    # Act
    response = client.post(LOGOUT_URL)

    # Assert
    assert response.status_code == HTTPStatus.OK
