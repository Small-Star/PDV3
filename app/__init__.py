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
from app.models import QS_Params

ingest_flag = "MERGE"

if ingest_flag == "FORCE":
    db.drop_all()

db.create_all()
num_rec = db.session.query(QS_Params).count()
logging.info("Loading database with %s records", num_rec)

if ingest_flag == "MERGE" or ingest_flag == "FORCE":
    logging.info("Ingesting mood data...")
    #ingest.ingest_mood()
    logging.info("Ingesting diet data...")
    #ingest.ingest_diet()
    logging.info("Ingesting heart rate data...")
    #ingest.ingest_rhr()
    logging.info("Ingesting sleep data...")
    #ingest.ingest_sleep()
    logging.info("Ingesting blood data...")
    #ingest.ingest_blood()
    logging.info("Ingesting LIFTS...")
    #ingest.ingest_weightlifting()
    logging.info("-------------")

num_rec = db.session.query(QS_Params).count()
logging.info("Database has %s records", num_rec)
