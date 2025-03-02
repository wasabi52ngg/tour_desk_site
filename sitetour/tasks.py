from celery import shared_task
from django.utils import timezone
from .models import TourSession

import logging

logger = logging.getLogger(__name__)


@shared_task
def update_session_status():
    sessions_to_update = TourSession.objects.filter(
        status=TourSession.ACT,
        end_datetime__lte=timezone.now()
    )
    updated_count = sessions_to_update.update(status=TourSession.END)

    logger.info(f'Обновлено {updated_count} сессий')
    return f'Обновлено {updated_count} сессий'