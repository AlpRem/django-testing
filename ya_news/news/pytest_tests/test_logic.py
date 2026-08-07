from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

COMMENT_TEXT = "Текст комментария"


def test_anonymous_user_cant_create_comment(client, news, detail):
    """Неавторизованный пользователь не может создать комментарий."""
    # Arrange
    form_data = {"text": COMMENT_TEXT}

    # Act
    client.post(detail, data=form_data)

    # Assert
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, detail):
    """Авторизованный пользователь может создать комментарий."""
    # Arrange
    form_data = {"text": COMMENT_TEXT}

    # Act
    response = author_client.post(detail, data=form_data)

    # Assert
    assertRedirects(response, f"{detail}#comments")
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail):
    """Комментарий с запрещенными словами не проходит валидацию."""
    # Arrange
    form_data = {"text": f"Какой-то текст {BAD_WORDS[0]} еще текст"}

    # Act
    response = author_client.post(detail, data=form_data)

    # Assert
    assertFormError(response.context["form"], "text", WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, comment, detail):
    """Автор может удалить свой комментарий."""
    # Arrange
    comments_count = Comment.objects.count()

    # Act
    response = author_client.delete(delete_url)

    # Assert
    assertRedirects(response, f"{detail}#comments")
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == comments_count - 1


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    """Пользователь не может удалить чужой комментарий."""
    # Arrange
    comments_count = Comment.objects.count()

    # Act
    response = reader_client.delete(delete_url)

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(author_client, edit_url, comment, detail):
    """Автор может редактировать свой комментарий."""
    # Arrange
    new_text = "Текст 2"

    # Act
    response = author_client.post(edit_url, data={"text": new_text})

    # Assert
    assertRedirects(response, f"{detail}#comments")
    comment.refresh_from_db()
    assert comment.text == new_text


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url,
        comment):
    """Пользователь не может редактировать чужой комментарий."""
    # Arrange
    new_text = "Текст 2"

    # Act
    response = reader_client.post(
        edit_url,
        data={"text": new_text}
    )

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == "Текст"
