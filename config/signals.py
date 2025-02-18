from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask
from celery.schedules import crontab

@receiver(post_migrate)
def create_periodic_tasks(sender, **kwargs):
    if sender.name == 'config':
        PeriodicTask.objects.get_or_create(
            name='Update payed status daily',
            task='config.tasks.update_payed_status',
            defaults={
                'crontab': crontab(hour=0, minute=0)  # Har kuni soat 00:00 da ishga tushadi
            }
        )

