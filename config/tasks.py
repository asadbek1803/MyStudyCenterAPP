from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from accounts.models import Account

@shared_task
def update_payed_status():
    threshold_date = timezone.now() - timedelta(days=30)
    accounts_to_update = Account.objects.filter(
        is_payed=True,
        last_payment_date__lte=threshold_date
    )
    count = accounts_to_update.update(is_payed=False)
    return count

