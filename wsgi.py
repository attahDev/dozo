"""
wsgi.py — single entry point for both dev and production

  Local dev:   python wsgi.py
  Production:  gunicorn wsgi:app --workers 2 --bind 0.0.0.0:8000
               (drop --preload — see comment below)
"""
import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

# ── Gunicorn hooks (ignored when running via `python wsgi.py`) ────────────────
#
# WHY NO --preload:
#   --preload forks workers AFTER the master loads the app. Any threads started
#   before the fork (like APScheduler) are silently killed in each worker.
#   Without --preload, each worker loads the app independently, so the
#   scheduler starts cleanly inside its own process — no hook needed.
#
# We restrict the scheduler to worker 0 only (via the worker_int env var
# Gunicorn sets) to avoid duplicate reminder emails from every worker.

def when_ready(server):
    """Called once in the Gunicorn master after the server is ready."""
    server.log.info("DOZO is up.")


def post_fork(server, worker):
    """
    Called in each worker after forking.
    Start APScheduler only in the first worker to prevent duplicate emails.
    """
    if worker.age == 0:
        from app import scheduler
        scheduler.start(app)
        server.log.info("Scheduler started in worker pid=%s", worker.pid)


def worker_exit(server, worker):
    """Cleanly shut down the scheduler when a worker exits."""
    try:
        from app import scheduler
        scheduler.stop()
    except Exception:
        pass


# ── Dev server ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Only reaches here via `python wsgi.py` — Gunicorn never runs this block.
    from app import scheduler
    scheduler.start(app)

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development'),
        use_reloader=False,  # required — APScheduler breaks with Flask reloader
    )