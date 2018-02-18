from html.parser import HTMLParser
import re, datetime, os, logging

from app import app, db
from app.models import Mood, QS_Params

from collections import namedtuple

Mood_Tup = namedtuple('Mood_Tup', 'date a_l a_u a_s v_l v_u v_s')
Diet_Tup = namedtuple('Diet_Tup', 'date kcal_intake intake_error_bar protein_intake protein_intake_error_bar carb_intake net_carb_intake tdee tdee_error_bar cycle_phase cycle_num')
Diet_Tup.__new__.__defaults__ = (-1,) * len(Diet_Tup._fields)
Rhr_Tup = namedtuple('Rhr_Tup', 'date rhr_time bpm')
Sleep_Tup = namedtuple('Sleep_Tup', 'date sleep_onset sleep_duration sleep_how_much_more sleep_how_deep sleep_interruptions sleep_overall_q sleep_notes')
Blood_Tup = namedtuple('Blood_Tup', 'date glucose_time glucose ketones_time ketones blood_notes')

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
            logging.warning("Validation error in mood ingest for date " + str(mt.date) + ": " + e.args[0])
            return Mood_Tup(date=datetime.date(2100,1,1), a_l=5,a_u=5,a_s='N',v_l=5,v_u=5,v_s='N')

    Mood_Parser = Mood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["MOOD_FILE"]), 'r')

    #Read data
    Mood_Parser.feed(f_name.read())
    t_a = Mood_Parser.get_moods()

    #Validate
    t_a_ = [val_mood_params(t) for t in t_a]

    #Try and add entry to db
    ad = 0;
    for _ in t_a_:
        if Mood.query.get(_.date) == None:
            #db.session.add(Mood(_.date,_.a_l,_.a_u,_.a_s,_.v_l,_.v_u,_.v_s))
            db.session.add(Mood(_.date,_.a_l,_.a_u,_.a_s,_.v_l,_.v_u,_.v_s))
            ad += 1

    logging.info("Ingested %s mood records; Validated %s mood records; Added %s mood records", str(len(t_a)), str(len(t_a_)), str(ad))

    db.session.commit()
    print("Mood Ingest complete")

def ingest_diet(date=""):
    '''Reads data from DIET_FILE and inputs it into db'''

    class Diet_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date, self.kcal_intake, self.intake_error_bar, self.protein_intake, self.protein_intake_error_bar, self.carb_intake, self.net_carb_intake, self.tdee, self.cycle_phase, self.cycle_num = datetime.date(2100,1,1), -1, -1, -1, -1, -1, -1, -1, "", -1

            self.date_re = re.compile(r'- \d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'
            self.calorie_intake_re = re.compile(r'\s*Intake: ')
            self.protein_intake_re = re.compile(r'\s*Protein: ')
            self.tdee_re = re.compile(r'\s*Est. TDEE: ')
            self.carb_re = re.compile(r'\s*Carbs: ')
            self.fic_re = re.compile(r'\S+') #Note, this pattern is used on the BACKWARDS TDEE string

        def handle_data(self, data):
            #Line by line parsing of input data
            if re.match(self.date_re,data) != None:
                self.date = datetime.datetime.strptime(data[2:-1],"%m/%d/%Y").date()
            elif re.match(self.calorie_intake_re,data) != None:
                self.kcal_intake = int(re.split(self.calorie_intake_re,re.split("kcal",data)[0])[1])
                self.intake_error_bar = int(re.findall("[0-9]*%",data)[0][:-1])
            elif re.match(self.protein_intake_re,data) != None:
                self.protein_intake = int(re.split(self.protein_intake_re,re.split("g",data)[0])[1])
                self.protein_intake_error_bar = int(re.findall("[0-9]*%",data)[0][:-1])
            elif re.match(self.carb_re,data) != None:
                ci, nci = re.findall("[0-9]*g",data)
                self.carb_intake = int(ci[:-1])
                self.net_carb_intake = int(nci[:-1])
            elif re.match(self.tdee_re,data) != None:
                self.tdee = int(re.split(self.tdee_re,re.split("kcal",data)[0])[1])#Match pattern, split away extraneous stuff
                self.cycle_phase = re.search(self.fic_re,data[-2::]).group()     #Pulls out the endmost non-whitespace character(s)

                #TDEEs are always the end of an entry; push the tuple to the to_add list
                self.to_add.append(Diet_Tup(date=self.date, kcal_intake=self.kcal_intake, intake_error_bar=self.intake_error_bar, protein_intake=self.protein_intake, protein_intake_error_bar=self.protein_intake_error_bar, carb_intake=self.carb_intake, net_carb_intake=self.net_carb_intake, tdee=self.tdee, cycle_phase=self.cycle_phase)) #Pull in the rest later

                #Reset vals
                self.date, self.kcal_intake, self.intake_error_bar, self.protein_intake, self.protein_intake_error_bar, self.carb_intake, self.net_carb_intake, self.tdee, self.cycle_phase, self.cycle_num = datetime.date(2100,1,1), -1, -1, -1, -1, -1, -1, -1, "", -1

        def get_diets(self):
            return self.to_add
    #Validate
    def val_diet_params(dt):
        CYCLE_PHASES = ['C', 'B', 'M', 'N', 'F', 'FB']
        try:
            assert type(dt.date)==datetime.date and dt.date >= datetime.date(2014,1,1), "date"
            assert dt.kcal_intake >=0, "kcal_intake"
            assert dt.intake_error_bar >=0, "intake_error_bar"
            assert dt.protein_intake >=0, "protein_intake"
            assert dt.protein_intake_error_bar >=0, "protein_intake_error_bar"
            assert dt.carb_intake >=0 or dt.date < datetime.date(2017,4,10), "carb_intake" #Note: 04/10/2017 is the start date for recording carb macros
            assert (dt.net_carb_intake >=0 and dt.net_carb_intake <= dt.carb_intake)  or dt.date < datetime.date(2017,4,10), "net_carb_intake"
            assert (dt.tdee >= 1600) or (dt.tdee == 0 and dt.date <= datetime.date(2015,4,6)), "tdee" #Note: 04/06/2015 is the start date for recording carb macros
            #assert dt.tdee_error_bar >=0, "tdee_error_bar" #Why is this here?
            assert dt.cycle_phase.upper() in CYCLE_PHASES, "cycle_phase"
            #assert dt.cycle_num >0 and dt.cycle_num < 100, "cycle_num" #TODO: Put this into the ingest
            return dt
        except Exception as e:
            logging.warning("Validation error in Diet ingest for date " + str(dt.date) + ": " + e.args[0])
            return Diet_Tup(date=datetime.date(2100,1,1), kcal_intake=-1, intake_error_bar=-1, protein_intake=-1, protein_intake_error_bar=-1, carb_intake=-1, net_carb_intake=-1, tdee=-1, tdee_error_bar=-1, cycle_phase="N", cycle_num=-1)


    Diet_Parser = Diet_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["DIET_FILE"]), 'r')

    #Read data
    Diet_Parser.feed(f_name.read())
    t_a = Diet_Parser.get_diets()
    #print("Days read: " + str(len(t_a)))
    t_a_ = [val_diet_params(t) for t in t_a]
    #print("Days passing validation: " + str(len(t_a_)))

    ad = 0
    #Try and add entry to db
    for _ in t_a_:
        if QS_Params.query.get(_.date) == None:
            q = QS_Params(_.date)
            db.session.add(q)

        q = QS_Params.query.get(_.date)
        q.kcal_intake = _.kcal_intake
        q.intake_error_bar = _.intake_error_bar
        q.protein_intake = _.protein_intake
        q.protein_intake_error_bar = _.protein_intake_error_bar
        q.carb_intake = _.carb_intake
        q.net_carb_intake = _.net_carb_intake
        q.tdee = _.tdee
        q.tdee_error_bar = _.tdee_error_bar
        q.cycle_phase = _.cycle_phase
        q.cycle_num = _.cycle_num

        q.compute_derived_vals()
        ad += 1

    db.session.commit()
    logging.info("Ingested %s diet records; Validated %s diet records; Added %s diet records", str(len(t_a)), str(len(t_a_)), str(ad))
    print("Diet Ingest complete")

def ingest_rhr(date=""):
    '''Reads data from RHR_FILE and inputs it into db'''

    class RHR_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date, self.rhr_time, self.bpm = datetime.date(2100,1,1), "01:01", -1

            self.date_re = re.compile(r'\d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'

        def handle_data(self, data):
            #Line by line parsing of input data
            data_ = data.strip()    #Drop whitespace
            if re.match(self.date_re,data_) != None:
                self.date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y").date()
                time_str = re.split(";",data_)[1]
                self.rhr_time = datetime.datetime.fromordinal((self.date.toordinal())) + datetime.timedelta(hours=int(time_str[0:2]),minutes=int(time_str[3:]))
                self.bpm = int(re.split(";",data_)[2][:-3])
                self.to_add.append(Rhr_Tup(date=self.date, rhr_time=self.rhr_time, bpm=self.bpm))

                #Reset vals
                self.date, self.rhr_time, self.bpm = datetime.date(2100,1,1), -1, -1

        def get_rhrs(self):
            return self.to_add

    #Validate
    def val_rhr_params(rt):
        try:
            assert type(rt.date)==datetime.date and rt.date >= datetime.date(2017,5,1), "date"
            assert rt.bpm > 40 and rt.bpm < 120, "bpm"
            assert type(rt.rhr_time)==datetime.datetime, "rhr_time"
            return rt
        except Exception as e:
            logging.warning("Validation error in RHR ingest for date " + str(rt.date) + ": " + e.args[0])
            return Rhr_Tup(date=datetime.date(2100,1,1), rhr_time=datetime.datetime(2100,1,1,1,1), bpm=-1)

    RHR_Parser = RHR_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["RHR_FILE"]), 'r')

    #Read data
    RHR_Parser.feed(f_name.read())
    t_a = RHR_Parser.get_rhrs()
    #print("Days read: " + str(len(t_a)))
    t_a_ = [val_rhr_params(t) for t in t_a]
    #print("Days passing validation: " + str(len(t_a_)))

    ad = 0
    #Try and add entry to db
    for _ in t_a_:
        if QS_Params.query.get(_.date) == None:
            q = QS_Params(_.date)
            db.session.add(q)

        q = QS_Params.query.get(_.date)
        q.rhr_time = _.rhr_time
        q.bpm = _.bpm

        ad += 1

    db.session.commit()
    logging.info("Ingested %s RHR records; Validated %s RHR records; Added %s RHR records", str(len(t_a)), str(len(t_a_)), str(ad))
    print("RHR Ingest complete")

def ingest_sleep(date=""):
    '''Reads data from SLEEP_FILE and inputs it into db'''

    class Sleep_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date, self.sleep_onset, self.sleep_duration, self.sleep_how_much_more, self.sleep_how_deep, self.sleep_interruptions, self.sleep_overall_q, self.sleep_notes = datetime.date(2100,1,1), "01:01", -1, -1, -1, -1, -1, ""

            self.date_re = re.compile(r'\d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'

        def handle_data(self, data):
            #Line by line parsing of input data
            data_ = data.strip()    #Drop whitespace
            if re.match(self.date_re,data_) != None:
                self.date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y").date()
                time_str = re.split(";",data_)[1]
                self.sleep_onset = datetime.datetime.fromordinal((self.date.toordinal())) + datetime.timedelta(hours=int(time_str[0:2]),minutes=int(time_str[3:]))
                self.sleep_duration = float(re.split(";",data_)[2])
                self.sleep_how_much_more = int(re.split(";",data_)[3])
                self.sleep_how_deep = int(re.split(";",data_)[4])
                self.sleep_interruptions = int(re.split(";",data_)[5])
                self.sleep_overall_q = int(re.split(";",data_)[6])
                if len(re.split(";",data_)) >= 8:
                    #print(self.date, len(data_))
                    self.sleep_notes = re.split(";",data_)[7][6:]
                else:
                    self.sleep_notes = ""
                self.to_add.append(Sleep_Tup(date=self.date, sleep_onset=self.sleep_onset, sleep_duration=self.sleep_duration, sleep_how_much_more=self.sleep_how_much_more, sleep_how_deep=self.sleep_how_deep, sleep_interruptions=self.sleep_interruptions, sleep_overall_q=self.sleep_overall_q, sleep_notes=self.sleep_notes))

                #Reset vals
                self.date, self.sleep_onset, self.sleep_duration, self.sleep_how_much_more, self.sleep_how_deep, self.sleep_interruptions, self.sleep_overall_q, self.sleep_notes = datetime.date(2100,1,1), "01:01", -1, -1, -1, -1, -1, ""

        def get_sleeps(self):
            return self.to_add

    #Validate
    def val_sleep_params(st):
        try:
            assert type(st.date)==datetime.date and st.date >= datetime.date(2017,4,17), "date"
            assert type(st.sleep_onset)==datetime.datetime, "sleep_onset"
            assert st.sleep_duration > 0 and st.sleep_duration < 16, "sleep_duration"
            assert st.sleep_how_much_more > 0 and st.sleep_how_much_more < 10, "sleep_how_much_more"
            assert st.sleep_how_deep > 0 and st.sleep_how_deep < 10, "sleep_how_deep"
            assert st.sleep_interruptions > 0 and st.sleep_interruptions < 10, "sleep_interruptions"
            assert st.sleep_overall_q > 0 and st.sleep_overall_q < 10, "sleep_overall_q"
            return st
        except Exception as e:
            logging.warning("Validation error in Sleep ingest for date " + str(st.date) + ": " + e.args[0])
            return Sleep_Tup(date=datetime.date(2100,1,1), sleep_onset=datetime.datetime(2100,1,1,1,1), sleep_duration=-1, sleep_how_much_more=-1, sleep_how_deep=-1, sleep_interruptions=-1, sleep_overall_q=-1, sleep_notes="")

    Sleep_Parser = Sleep_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["SLEEP_FILE"]), 'r')

    #Read data
    Sleep_Parser.feed(f_name.read())
    t_a = Sleep_Parser.get_sleeps()
    #print("Days read: " + str(len(t_a)))
    t_a_ = [val_sleep_params(t) for t in t_a]
    #print("Days passing validation: " + str(len(t_a_)))

    ad = 0
    #Try and add entry to db
    for _ in t_a_:
        if QS_Params.query.get(_.date) == None:
            q = QS_Params(_.date)
            db.session.add(q)

        q = QS_Params.query.get(_.date)
        q.sleep_onset = _.sleep_onset
        q.sleep_duration = _.sleep_duration
        q.sleep_how_much_more = _.sleep_how_much_more
        q.sleep_how_deep = _.sleep_how_deep
        q.sleep_interruptions = _.sleep_interruptions
        q.sleep_overall_q = _.sleep_overall_q
        q.sleep_notes = _.sleep_notes

        ad += 1

    db.session.commit()
    logging.info("Ingested %s Sleep records; Validated %s Sleep records; Added %s Sleep records", str(len(t_a)), str(len(t_a_)), str(ad))
    print("Sleep Ingest complete")

def ingest_blood(date=""):
    '''Reads data from BLOOD_FILE and inputs it into db'''

    class Blood_HTML_Parser(HTMLParser):
        ''' Input an xml file, return a list of tuples to add to the db'''
        def __init__(self):
            HTMLParser.__init__(self)

            self.to_add = [] #List of tuples that will be returned for adding to the db
            self.date, self.glucose_time, self.glucose, self.ketones_time, self.ketones, self.blood_notes = datetime.date(2100,1,1), None, None, None, None, ""

            self.k_g_toggle = 'g'

            self.date_re = re.compile(r'\d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'
            self.notes_re = re.compile(r'- Notes - (?P<blood_notes_g>.*)')
            self.glucose_re = re.compile(r'- (?P<glucose_time_g>\d\d:\d\d) - Blood Glucose: (?P<glucose_g>\d+) mg/dl')
            self.ketones_re = re.compile(r'- (?P<ketones_time_g>\d\d:\d\d) - Ketones: (?P<ketones_g>\d*.\d*)mmol/l')
        def handle_data(self, data):
            #Line by line parsing of input data
            #TODO: Pull in second/third/etc. measurements
            data_ = data.strip()    #Drop whitespace
            if re.match(self.date_re,data_) != None:
                self.to_add.append(Blood_Tup(date=self.date, glucose_time=self.glucose_time, glucose=self.glucose, ketones_time=self.ketones_time, ketones=self.ketones, blood_notes=self.blood_notes))
                self.date, self.glucose_time, self.glucose, self.ketones_time, self.ketones, self.blood_notes = datetime.date(2100,1,1), None, None, None, None, ""
                self.date = datetime.datetime.strptime(data_[:10],"%m/%d/%Y").date()
            elif (re.match(self.glucose_re,data_) != None) and (self.glucose == None): #Conditional makes sure second/third values do not overwrite morning reading
                _ = re.search(self.glucose_re,data_)
                g = _.group('glucose_time_g')
                self.glucose_time = datetime.datetime.fromordinal((self.date.toordinal())) + datetime.timedelta(hours=int(g[0:2]),minutes=int(g[3:]))
                self.glucose = int(_.group('glucose_g'))
            elif (re.match(self.ketones_re,data_) != None) and (self.ketones == None): #Conditional makes sure second/third values do not overwrite morning reading
                _ = re.search(self.ketones_re,data_)
                g = _.group('ketones_time_g')
                self.ketones_time = datetime.datetime.fromordinal((self.date.toordinal())) + datetime.timedelta(hours=int(g[0:2]),minutes=int(g[3:]))
                self.ketones = float(_.group('ketones_g'))
            elif re.match(self.notes_re, data_):
                self.blood_notes = re.search(self.notes_re,data_).group('blood_notes_g')

        def get_bloods(self):
            self.to_add.append(Blood_Tup(date=self.date, glucose_time=self.glucose_time, glucose=self.glucose, ketones_time=self.ketones_time, ketones=self.ketones, blood_notes=self.blood_notes))
            return self.to_add[1:]

    #Validate
    def val_blood_params(bt):
        try:
            assert type(bt.date)==datetime.date and bt.date >= datetime.date(2017,4,10), "date"
            if bt.glucose_time != None:
                assert type(bt.glucose_time)==datetime.datetime, "glucose_time"
                assert bt.glucose > 40 and bt.glucose < 200, "glucose"
            if bt.ketones_time != None:
                assert type(bt.ketones_time)==datetime.datetime, "ketones_time"
                assert bt.ketones > 0 and bt.ketones < 9, "ketones"
            assert type(bt.blood_notes)==str, "blood_notes"
            return bt
        except Exception as e:
            logging.warning("Validation error in Blood ingest for date " + str(bt.date) + ": " + e.args[0])
            return Blood_Tup(date=datetime.date(2100,1,1), glucose_time=None, glucose=None, ketones_time=None, ketones=None, blood_notes="")

    Blood_Parser = Blood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["BLOOD_FILE"]), 'r')

    #Read data
    Blood_Parser.feed(f_name.read())
    t_a = Blood_Parser.get_bloods()
    #print("Days read: " + str(len(t_a)))
    t_a_ = [val_blood_params(t) for t in t_a]
    #print("Days passing validation: " + str(len(t_a_)))

    ad = 0
    #Try and add entry to db
    for _ in t_a_:
        if QS_Params.query.get(_.date) == None:
            q = QS_Params(_.date)
            db.session.add(q)

        q = QS_Params.query.get(_.date)
        q.glucose_time = _.glucose_time
        q.glucose = _.glucose
        q.ketones_time = _.ketones_time
        q.ketones = _.ketones
        q.blood_notes = _.blood_notes

        ad += 1

    db.session.commit()
    logging.info("Ingested %s Blood records; Validated %s Blood records; Added %s Blood records", str(len(t_a)), str(len(t_a_)), str(ad))
    print("Blood Ingest complete")
