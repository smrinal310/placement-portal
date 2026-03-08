from celery import Celery
from celery.schedules import crontab

celery = Celery(__name__)


BEAT_SCHEDULE = {
    "send-daily-interview-reminders": {
        "task": "src.jobs.tasks.send_daily_interview_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    "send-monthly-placement-report": {
        "task": "src.jobs.tasks.send_monthly_placement_report",
        "schedule": crontab(hour=7, minute=0, day_of_month=1),
    },
}


def make_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        timezone=app.config.get("CELERY_TIMEZONE", "Asia/Kolkata"),
        task_serializer=app.config.get("CELERY_TASK_SERIALIZER", "json"),
        result_serializer=app.config.get("CELERY_RESULT_SERIALIZER", "json"),
        accept_content=app.config.get("CELERY_ACCEPT_CONTENT", ["json"]),
        beat_schedule=BEAT_SCHEDULE,
    )

    class ContextTask(celery.Task):
        """Ensure every task runs inside the Flask app context."""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
