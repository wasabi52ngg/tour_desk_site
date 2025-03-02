# your_project/celery.py
import os
from celery import Celery
from celery.schedules import crontab

# Указываем Django settings модуль для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_desk.settings')

# Создаем экземпляр Celery
app = Celery('tour_desk')

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи (tasks.py в приложениях)
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'update-session-status-every-minute': {
        'task': 'sitetour.tasks.update_session_status',  # Путь к задаче
        'schedule': crontab(minute='*'),  # Запускать каждую минуту
    },
}