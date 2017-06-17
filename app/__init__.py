from flask import Flask
from flask_sqlalchemy import SQLAlchemy

print("poop3")
app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models, ingest

ingest.ingest_mood()
