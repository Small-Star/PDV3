from html.parser import HTMLParser
import re, datetime, os

from app import app

def ingest_mood(date=""):

    #TODO: date scope
    #TODO: data validation

    Mood_Parser = Mood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["MOOD_FILE"]), 'r')
    Mood_Parser.feed(f_name.read())

    return Mood_Parser.get_moods()

class Mood_HTML_Parser(HTMLParser):
    ''' Input an xml file, return a list of tuples to add to the db'''
    def __init__(self):
        HTMLParser.__init__(self)

        self.to_add = [] #List of tuples that will be returned for adding to the db

        self.date_str_re = re.compile(r'\d\d\/\d\d\/\d\d')

    def handle_data(self, data):
        data_ = data.strip()    #Drop whitespace

        if re.match(self.date_str_re,data_) != None:
            #date_str = str(re.split('/',data_[:10])) #Remove cruft from date
            date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y")

            #Add (date,a_l,a_u,a_s,v_l,v_u,v_s)
            self.to_add.append((date,(int(data_[14]),int(data_[16]),data_[17]),(int(data_[20]),int(data_[22]),data_[23])))

    def get_moods(self):
        return self.to_add
