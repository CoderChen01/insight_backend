from celery import shared_task
from incident.models import Incident


@shared_task(ignore_result=True)
def clear_incidents():
    Incident.objects.all().delete()
