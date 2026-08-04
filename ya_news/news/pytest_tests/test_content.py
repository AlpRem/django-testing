from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE

def test_news_order(client, news_list):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)

def test_comments_order(client, news, comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news_object = response.context['news']
    all_comments = news_object.comment_set.all()
    all_timestamps = [
        comment.created for comment in all_comments
    ]
    assert all_timestamps == sorted(all_timestamps)

def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context

def test_authorized_client_has_form(client, news, author):
    client.force_login(author)
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)