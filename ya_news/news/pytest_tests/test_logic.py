from http import HTTPStatus

from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects

COMMENT_TEXT = "Текст комментария"


def test_anonymous_user_cant_create_comment(client, news, detail):
    """Тест проверки отсутствия возможности добавления комментария у неавторизованного пользователя"""
    form_data = {"text": COMMENT_TEXT}
    client.post(detail, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, detail):
    """Тест проверки возможности добавления комментария для авторизованного пользователя"""
    form_data = {"text": COMMENT_TEXT}
    response = author_client.post(detail, data=form_data)
    assertRedirects(response, f"{detail}#comments")
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail):
    """Тест блокировки стоп-слов"""
    form_data = {"text": f"Какой-то текст {BAD_WORDS[0]} еще текст"}
    response = author_client.post(detail, data=form_data)
    assertFormError(response.context["form"], "text", WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, comment, detail):
    """Тест проверки удаления комментариев для автора"""
    response = author_client.delete(delete_url)
    assertRedirects(response, f"{detail}#comments")
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    """Тест невозможности удаления комментариев для не автора"""
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, edit_url, comment, detail):
    """Тест проверки редактирования для автора"""
    new_text = "Текст 2"
    response = author_client.post(edit_url, data={"text": new_text})
    assertRedirects(response, f"{detail}#comments")
    comment.refresh_from_db()
    assert comment.text == new_text


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url,
        comment):
    """Тест невозможности редактирования комментариев для не авторов"""
    response = reader_client.post(
        edit_url,
        data={"text": "Текст 2"}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == "Текст"
