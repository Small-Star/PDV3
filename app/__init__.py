from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging


app = Flask(__name__)

app.config.from_object('config')

logging.basicConfig(filename=app.config["LOG_FILE"], level=logging.DEBUG, format='%(levelname)s: %(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

logging.info("-------------")
logging.info("Loading db...")
db = SQLAlchemy(app)


from app import views, models, ingest
db.create_all()
logging.info("Ingesting mood data...")
ingest.ingest_mood()
logging.info("Ingesting diet data...")
ingest.ingest_diet()
logging.info("Ingesting heart rate data...")
ingest.ingest_rhr()
logging.info("Ingesting sleep data...")
ingest.ingest_sleep()

logging.info("-------------")
