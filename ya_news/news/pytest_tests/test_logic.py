from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'

def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0

def test_user_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author

def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    form_data = {
        'text': f'Какой-то текст {BAD_WORDS[0]} еще текст'
    }
    response = author_client.post(url, data=form_data)
    assertFormError(
        response.context['form'],
        'text',
        WARNING
    )
    assert Comment.objects.count() == 0

def test_author_can_delete_comment(
        author_client,
        delete_url,
        comment
):
    url_to_comments = reverse(
        'news:detail',
        args=(comment.news.id,)
    ) + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0

def test_user_cant_delete_comment_of_another_user(
        reader_client,
        delete_url
):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

def test_author_can_edit_comment(
        author_client,
        edit_url,
        comment
):
    new_text = 'Текст 2'
    response = author_client.post(edit_url, data={'text': new_text})
    url_to_comments = reverse(
        'news:detail',
        args=(comment.news.id,)
    ) + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_text

def test_user_cant_edit_comment_of_another_user(
        reader_client,
        edit_url,
        comment
):
    response = reader_client.post(
        edit_url,
        data={'text': 'Текст 2'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст'
