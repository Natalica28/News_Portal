from django_apscheduler.models import DjangoJobExecution

from NewsPaper import settings
from .models import Post, Subscriber
from celery import shared_task
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

SITE_URL = 'http://127.0.0.1:8000'
DEFAULT_FROM_EMAIL = "example@yandex.ru"

@shared_task()
def send_weekly_article_list():
    current_date = datetime.now()
    last_execution = DjangoJobExecution.objects.filter(job__id = 'send_weekly_article_list').last()
    if last_execution:
        last_execution_date = last_execution.run_etime.astimezone(timezone(settings.TIME_ZONE))
    else:
        last_execution_date = current_date - timedelta(weeks = 1)
    new_articles = Post.objects.filter(datetime__gt=last_execution_date)

    articles_by_category = {}
    for article in new_articles:
        for category in article.postCategory.all():
            articles_by_category.setdefault(category, []).append(article)

    for category, articles in articles_by_category.items():
        subscribers = Subscriber.objects.filter(category=category)
        if subscribers:
            subject = f'Новые статьи в категории {category.name_category}'
            text_content = 'Новые статьи:\n\n'
            for article in articles:
                text_content += f'{article.head}\n{article.get_absolute_url()}\n\n'

            for subscriber in subscribers:
                msg = EmailMultiAlternatives(subject, text_content, None, [subscriber.user.email])
                msg.send()

    if last_execution:
        last_execution.run_etime = current_date
        last_execution.save()
    else:
        DjangoJobExecution(job_id = 'send_weekly_article_list', run_etime = current_date).save()


@shared_task
def process_post_category_changed(post_id):
    instance = Post.objects.get(pk=post_id)
    category_names = instance.choice_category.all().values_list('name', flat = True)
    category_names_str = ', '.join(category_names)
    subscribers = User.objects.filter(subscriptions__category__in = instance.postCategory.all()).distinct()

    subject = f'Вышла новая новость в категории {category_names_str}'
    text_content = (
        f'Заголовок: {instance.title}\n'
        f'Текст: {instance.text}\n\n'
        f'Ссылка на новость: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )

    for subscriber in subscribers:
        msg = EmailMultiAlternatives(subject, text_content, None, [subscriber.email])
        msg.send()