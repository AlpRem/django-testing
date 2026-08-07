from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from ya_news.news.pytest_tests.urls import HOME_URL, LOGOUT_URL


@pytest.mark.parametrize(
    "public_url",
    [
        "home_url",
        "detail",
    ],
)
def test_public_pages(client, news, request, public_url):
    """Страницы новости и главна доступны всем пользователям."""
    # Arrange
    url = (
        HOME_URL
        if public_url == "home_url"
        else request.getfixturevalue(public_url)
    )

    # Act
    response = client.get(url)

    # Assert
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
    # Arrange
    test_client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=(comment.id,))

    # Act
    response = test_client.get(url)

    # Assert
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
    # Arrange
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.id,))
    redirect_url = f"{login_url}?next={url}"

    # Act
    response = client.get(url)

    # Assert
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
    # Arrange
    url = reverse(name)

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == HTTPStatus.OK


def test_logout_page(client):
    """Страница выхода доступна для всех пользователей."""
    # Act
    response = client.post(LOGOUT_URL)

    # Assert
    assert response.status_code == HTTPStatus.OK
