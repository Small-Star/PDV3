import os
basedir = os.path.abspath(os.path.dirname(__file__))

#DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

#Web Forms
WTF_CSRF_ENABLED = True
SECRET_KEY = 'sdhdzfkjlvnaohoaidfhnslkajbfvlzjxcvklzjdbfhouybf'

#File locations
BASE_FDIR = ""
MOOD_FILE = "mood/records/page.html"
