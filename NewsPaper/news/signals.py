from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import PostCategory, Subscriber

SITE_URL = 'http://127.0.0.1:8000'
DEFAULT_FROM_EMAIL = "example@yandex.ru"

def send_notifications(preview, pk, head, subscribers):
    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': preview,
            'link': f'{SITE_URL}/news/{pk}'
        }
    )

    msg = EmailMultiAlternatives(
        subject=head,
        body='',
        from_email=DEFAULT_FROM_EMAIL,
        to=subscribers,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(instance, action, **kwargs):
    if action == 'post_add':
        categories = instance.choice_category.all()
        subscribers_emails = []

        for cat in categories:
            subscribers = Subscriber.objects.filter(category=cat)
            for sub in subscribers:
                if sub.user.email:
                    subscribers_emails.append(sub.user.email)

        send_notifications(instance.preview(), instance.pk, instance.head, subscribers_emails)