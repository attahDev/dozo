
import logging
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

log = logging.getLogger(__name__)
_scheduler = None


def _check_reminders(app):
    with app.app_context():
        from app import db
        from app.models import Todo, User
        from app.email import send_reminder, send_overdue

        mins   = app.config['REMINDER_MINUTES_BEFORE']
        now    = datetime.utcnow()
        today  = date.today()
        window = now + timedelta(minutes=mins)

        due_soon = Todo.query.filter_by(completed=False, reminder_sent=False)\
                             .filter(Todo.due_date == today).all()
        for task in due_soon:
            if task.due_time:
                due_dt = datetime.combine(task.due_date, task.due_time)
                if not (now <= due_dt <= window):
                    continue
            user = User.query.get(task.user_id)
            if user and send_reminder(user, task):
                task.reminder_sent = True

        overdue = Todo.query.filter_by(completed=False, overdue_sent=False)\
                            .filter(Todo.due_date < today).all()
        for task in overdue:
            user = User.query.get(task.user_id)
            if user and send_overdue(user, task):
                task.overdue_sent = True

        db.session.commit()
        log.debug('Reminders: %d due, %d overdue', len(due_soon), len(overdue))


def _send_digests(app):
    with app.app_context():
        from app.models import User, Todo
        from app.email import send_digest

        today    = date.today()
        week_out = today + timedelta(days=7)

        for user in User.query.filter_by(notify_digest=True).all():
            send_digest(
                user,
                overdue   = Todo.query.filter_by(user_id=user.id, completed=False).filter(Todo.due_date < today).order_by(Todo.due_date).all(),
                due_today = Todo.query.filter_by(user_id=user.id, completed=False).filter(Todo.due_date == today).all(),
                upcoming  = Todo.query.filter_by(user_id=user.id, completed=False).filter(Todo.due_date > today, Todo.due_date <= week_out).limit(10).all(),
            )


def start(app):
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    interval = app.config.get('SCHEDULER_INTERVAL_MINS', 15)
    _scheduler = BackgroundScheduler(timezone='UTC', daemon=True)

    _scheduler.add_job(_check_reminders, IntervalTrigger(minutes=interval),
                       args=[app], id='reminders', replace_existing=True, misfire_grace_time=300)
    _scheduler.add_job(_send_digests, CronTrigger(hour=9, minute=0),
                       args=[app], id='digest',    replace_existing=True, misfire_grace_time=600)

    _scheduler.start()
    log.info('Scheduler started — reminders every %dm, digest at 09:00 UTC', interval)


def stop():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        