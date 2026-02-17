import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

def when_ready(server):
    server.log.info("DOZO is up.")


def post_fork(server, worker):
    if worker.age == 0:
        from app import scheduler
        scheduler.start(app)
        server.log.info("Scheduler started in worker pid=%s", worker.pid)


def worker_exit(server, worker):
    try:
        from app import scheduler
        scheduler.stop()
    except Exception:
        pass


if __name__ == '__main__':
    from app import scheduler
    scheduler.start(app)

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development'),
        use_reloader=False, 
    )