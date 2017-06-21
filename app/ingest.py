from html.parser import HTMLParser
import re, datetime, os

from app import app, db
from app.models import Mood

MOOD_S = ['L','U','M','N']

def ingest_mood(date=""):
    '''Reads data from MOOD_FILE and inputs it into db'''
    Mood_Parser = Mood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["MOOD_FILE"]), 'r')

    #Read data
    Mood_Parser.feed(f_name.read())
    t_a = Mood_Parser.get_moods()

    #Validate
    t_a_ = [t for t in t_a if (type(t[0])==datetime.date and (t[1] > 0) and (t[1] < 10) and (t[2] > 0) and (t[2] < 10) and (t[3] in MOOD_S) == True and (t[4] > 0) and (t[4] < 10) and (t[5] > 0) and (t[5] < 10) and (t[6] in MOOD_S) == True)]
    if len(t_a_) != len(t_a):
        print("Validation error")
    
    #Try and add entry to db
    for _ in t_a_:
        if Mood.query.get(_[0]) == None:
            db.session.add(Mood(_[0],_[1],_[2],_[3],_[4],_[5],_[6]))
            print("Adding: " + str(_[0]))
        else:
            print("Duplicate: " + str(_[0]))

    db.session.commit()
    print("Mood Ingest complete")

class Mood_HTML_Parser(HTMLParser):
    ''' Input an xml file, return a list of tuples to add to the db'''
    def __init__(self):
        HTMLParser.__init__(self)

        self.to_add = [] #List of tuples that will be returned for adding to the db

        self.date_str_re = re.compile(r'\d\d\/\d\d\/\d\d')

    def handle_data(self, data):
        data_ = data.strip()    #Drop whitespace

        if re.match(self.date_str_re,data_) != None:
            date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y").date()
            self.to_add.append((date,int(data_[14]),int(data_[16]),data_[17],int(data_[20]),int(data_[22]),data_[23]))

    def get_moods(self):
        return self.to_add
