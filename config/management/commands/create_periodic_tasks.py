from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask
from celery.schedules import crontab
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create periodic tasks'

    def handle(self, *args, **kwargs):
        # Rejalashtirilgan vazifani yaratish
        PeriodicTask.objects.create(
            name='Update payed status daily',
            task='config.tasks.update_payed_status',
            crontab=crontab(hour=0, minute=0)  # Har kuni soat 00:00 da ishga tushadi
        )
        self.stdout.write(self.style.SUCCESS('Successfully created periodic tasks'))


