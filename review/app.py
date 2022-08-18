from flask import Flask
from celery.utils.log import get_task_logger
from twiiter_data_fetch import fetch_data
from datetime import timedelta


logger = get_task_logger(__name__)


app = Flask(__name__)

app.run(debug = True)