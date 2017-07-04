from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import sys, datetime
sys.path.insert(0, './app')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/u_delta/projects/PDV3/app.db'
db = SQLAlchemy(app)

from app.models import Mood, QS_Params


db.create_all()
print("Current table:")

##
##ms = Mood.query.all()
##print(ms)
##
##print("Adding some test users")
##
###db.session.add(Mood(datetime.date(2001,5,20),1,3,'M',4,6,'N'))
###db.session.add(Mood(datetime.date(2005,6,21),2,4,'N',5,7,'U'))
db.session.commit()
