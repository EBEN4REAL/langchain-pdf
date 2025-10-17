import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SESSION_PERMANENT = True
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    UPLOAD_URL = "https://prod-upload-langchain.fly.dev"
    CELERY = {
        "broker_url": "redis://localhost:6379/0",
        "task_ignore_result": True,
        "broker_connection_retry_on_startup": False,
    }
