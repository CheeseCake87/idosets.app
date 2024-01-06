import logging

from huey import SqliteHuey

run = SqliteHuey(filename="app_flask/instance/huey.db")

logging.getLogger("huey").setLevel(logging.DEBUG)


def load_tasks():
    from .tasks import send_email

    _ = [send_email]


load_tasks()
