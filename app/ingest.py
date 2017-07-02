from html.parser import HTMLParser
import re, datetime, os

from app import app, db
from app.models import Mood, QS_Params

from collections import namedtuple

Mood_Tup = namedtuple('Mood_Tup', 'date a_l a_u a_s v_l v_u v_s')
Diet_Tup = namedtuple('Diet_Tup', 'date kcal_intake protein_intake protein_intake_error_bar carbs_intake net_carbs_intake tdee tdee_error_bar cycle_phase cycle_num')
Diet_Tup.__new__.__defaults__ = (-1,) * len(Diet_Tup._fields)

def ingest_mood(date=""):
    '''Reads data from MOOD_FILE and inputs it into db'''

    class Mood_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date_str_re = re.compile(r'\d\d\/\d\d\/\d\d')

        def handle_data(self, data):
            data_ = data.strip()    #Drop whitespace

            if re.match(self.date_str_re,data_) != None:
                self.to_add.append(Mood_Tup(date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y").date(), a_l = int(data_[14]), a_u = int(data_[16]), a_s = data_[17], v_l = int(data_[20]), v_u = int(data_[22]), v_s = data_[23]))

        def get_moods(self):
            return self.to_add

    def val_mood_params(mt):
        MOOD_S = ['L','U','M','N']
        try:
            assert type(mt.date)==datetime.date and mt.date >= datetime.date(2015,11,30), "date"
            assert mt.a_l > 0 and mt.a_l < 10 and mt.a_u > 0 and mt.a_u < 10 and mt.v_l > 0 and mt.v_l < 10 and mt.v_u > 0 and mt.v_u < 10, "numeric value"
            assert mt.a_s in MOOD_S and mt.v_s in MOOD_S, "s value"
            return mt
        except Exception as e:
            print("Validation error in mood ingest for date " + str(mt.date) + ": " + e.args[0])
            return Mood_Tup(date=datetime.date(2100,1,1), a_l=5,a_u=5,a_s='N',v_l=5,v_u=5,v_s='N')

    Mood_Parser = Mood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["MOOD_FILE"]), 'r')

    #Read data
    Mood_Parser.feed(f_name.read())
    t_a = Mood_Parser.get_moods()

    #Validate
    t_a_ = [val_mood_params(t) for t in t_a]

    #Try and add entry to db
    for _ in t_a_:
        if Mood.query.get(_.date) == None:
            db.session.add(Mood(_.date,_.a_l,_.a_u,_.a_s,_.v_l,_.v_u,_.v_s))
            #print("Adding: " + str(_.date))
        #else:
            #print("Duplicate: " + str(_.date))

    db.session.commit()
    print("Mood Ingest complete")

def ingest_diet(date=""):
    '''Reads data from DIET_FILE and inputs it into db'''

    class Diet_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date, self.kcal_intake, self.protein_intake, self.protein_intake_error_bar, self.carbs_intake, self.net_carbs_intake, self.tdee, self.tdee_error_bar, self.cycle_phase, self.cycle_num = datetime.date(2100,1,1), -1, -1, -1, -1, -1, -1, -1, "", -1

            self.date_re = re.compile(r'- \d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'
            self.calorie_intake_re = re.compile(r'\s*Intake: ')
            self.protein_intake_re = re.compile(r'\s*Protein: ')
            self.tdee_re = re.compile(r'\s*Est. TDEE: ')
            self.fic_re = re.compile(r'\S+') #Note, this pattern is used on the BACKWARDS TDEE string

        def handle_data(self, data):
            #Line by line parsing of input data
            if re.match(self.date_re,data) != None:
                self.date = datetime.datetime.strptime(data[2:-1],"%m/%d/%Y").date()
            elif re.match(self.calorie_intake_re,data) != None:
                self.kcal_intake = int(re.split(self.calorie_intake_re,re.split("kcal",data)[0])[1])
            elif re.match(self.protein_intake_re,data) != None:
                self.protein_intake = int(re.split(self.protein_intake_re,re.split("g",data)[0])[1])
            elif re.match(self.tdee_re,data) != None:
                self.tdee = int(re.split(self.tdee_re,re.split("kcal",data)[0])[1])#Match pattern, split away extraneous stuff
                self.cycle_phase = re.search(self.fic_re,data[-2::]).group()     #Pulls out the endmost non-whitespace character(s)

                #TDEEs are always the end of an entry; push the tuple to the to_add list
                self.to_add.append(Diet_Tup(date=self.date, kcal_intake=self.kcal_intake, protein_intake=self.protein_intake, tdee=self.tdee, cycle_phase=self.cycle_phase)) #Pull in the rest later

                #Reset vals
                self.date, self.kcal_intake, self.protein_intake, self.protein_intake_error_bar, self.carbs_intake, self.net_carbs_intake, self.tdee, self.tdee_error_bar, self.cycle_phase, self.cycle_num = datetime.date(2100,1,1), -1, -1, -1, -1, -1, -1, -1, "", -1

        def get_diets(self):
            return self.to_add
    #Validate
    def val_diet_params(dt):
        #***TODO: Valiadate
        return dt

    Diet_Parser = Diet_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["DIET_FILE"]), 'r')

    #Read data
    Diet_Parser.feed(f_name.read())
    t_a = Diet_Parser.get_diets()
    #print("Days read: " + str(len(t_a)))
    t_a_ = [val_diet_params(t) for t in t_a]
    #print("Days passing validation: " + str(len(t_a_)))

    #ad, nad = 0,0
    #Try and add entry to db
    for _ in t_a_:
        if QS_Params.query.get(_.date) == None:
            db.session.add(QS_Params(_.date, _.kcal_intake, _.protein_intake, _.protein_intake_error_bar, _.carbs_intake, _.net_carbs_intake, _.tdee, _.tdee_error_bar, _.cycle_phase, _.cycle_num))
            #print("Adding QS Param: " + str(_.date) + str(_.kcal_intake))
            #ad += 1
        #else:
            #print("Duplicate QS Param: " + str(_.date))
            #nad += 1

    #print("Added: " + str(ad) + "\nNot Added: " + str(nad) +" of "+ str(len(t_a)) + " " + str(len(t_a_)))

    db.session.commit()
    print("Diet Ingest complete")
