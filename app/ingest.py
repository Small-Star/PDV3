from html.parser import HTMLParser
import re, datetime, os

from app import app, db
from app.models import Mood

from collections import namedtuple

Mood_Tup = namedtuple('Mood_Tup', 'date a_l a_u a_s v_l v_u v_s')
def ingest_mood(date=""):
    '''Reads data from MOOD_FILE and inputs it into db'''
    Mood_Parser = Mood_HTML_Parser()
    f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["MOOD_FILE"]), 'r')

    #Read data
    Mood_Parser.feed(f_name.read())
    t_a = Mood_Parser.get_moods()

    #Validate
    MOOD_S = ['L','U','M','N']

    def val_mood_params(mt):
        try:
            assert type(mt.date)==datetime.date and mt.date >= datetime.date(2015,11,30), "date"
            assert mt.a_l > 0 and mt.a_l < 10 and mt.a_u > 0 and mt.a_u < 10 and mt.v_l > 0 and mt.v_l < 10 and mt.v_u > 0 and mt.v_u < 10, "numeric value"
            assert mt.a_s in MOOD_S and mt.v_s in MOOD_S, "s value"
            return mt
        except Exception as e:
            print("Validation error in mood ingest for date " + str(mt.date) + ": " + e.args[0])
            return Mood_Tup(date=datetime.date(2100,1,1), a_l=5,a_u=5,a_s='N',v_l=5,v_u=5,v_s='N')

    t_a_ = [val_mood_params(t) for t in t_a]

    #Try and add entry to db
    for _ in t_a_:
        if Mood.query.get(_.date) == None:
            db.session.add(Mood(_.date,_.a_l,_.a_u,_.a_s,_.v_l,_.v_u,_.v_s))
            #print("Adding: " + str(_.date))
        else:
            print("Duplicate: " + str(_.date))

    db.session.commit()
    print("Mood Ingest complete")



# def ingest_diet(date=""):
#     '''Reads data from DIET_FILE and inputs it into db'''
#     Diet_Parser = Diet_HTML_Parser()
#     f_name = open(os.path.join(app.config["BASE_FDIR"], app.config["DIET_FILE"]), 'r')
#
#     #Read data
#     Diet_Parser.feed(f_name.read())
#     t_a = Diet_Parser.get_diet_vals()
#
#     #Validate
#     #***TODO: validate
#
#     #Try and add entry to db
#     for _ in t_a_:
#         if QS_Params.query.get(_[0]) == None:
#             db.session.add(QS_Params(_[0])
#             print("Adding QS Param: " + str(_[0]))
#         else:
#             print("Duplicate QS Param: " + str(_[0]))
#
#     db.session.commit()
#     print("Diet Ingest complete")

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
#
# class Diet_HTML_Parser(HTMLParser):
#     ''' Input an xml file, return a list of tuples to add to the db'''
#     def __init__(self):
#         HTMLParser.__init__(self)
#
#         self.to_add = [] #List of tuples that will be returned for adding to the db
#         self.calorie_intake = []
#         self.protein_intake = []
#         self.tdee = []
#         self.day_nodes = collections.OrderedDict()
#
#         self.date_re = re.compile(r'- \d\d\/\d\d\/\d\d\d\d')      #ex: '03/22/2014'
#         self.calorie_intake_re = re.compile(r'\s*Intake: ')
#         self.protein_intake_re = re.compile(r'\s*Protein: ')
#         self.tdee_re = re.compile(r'\s*Est. TDEE: ')
#         self.fic_re = re.compile(r'\S+') #Note, this pattern is used on the BACKWARDS TDEE string
#
#     def handle_data(self, data):
#         #Line by line parsing of input data
#         if re.match(self.date_re,data) != None:
#             day_str_list = re.split('/',data[2:-1]) #Remove cruft from date
#             self.current_date = datetime.date(int(day_str_list[2]),int(day_str_list[0]),int(day_str_list[1]))
#             new_day_node = day_node(self.current_date)
#             self.day_nodes[self.current_date.toordinal()] = new_day_node
#             self.day_nodes[new_day_node.get_date().toordinal()] = new_day_node #Add new date to dict: key is the ordinal date
#         elif re.match(self.calorie_intake_re,data) != None:
#             node = self.day_nodes.get(self.current_date.toordinal(),day_node(datetime.date(1000,01,01))) #01/01/1000 denotes an error
#             cal_int = int(re.split(self.calorie_intake_re,re.split("kcal",data)[0])[1])#Match pattern, split away extraneous stuff
#             node.set_calorie_intake(cal_int)
#             self.calorie_intake.append(cal_int)
#         elif re.match(self.protein_intake_re,data) != None:
#             node = self.day_nodes.get(self.current_date.toordinal(),day_node(datetime.date(1000,01,01))) #01/01/1000 denotes an error
#             pro_int = int(re.split(self.protein_intake_re,re.split("g",data)[0])[1])#Match pattern, split away extraneous stuff
#             node.set_protein_intake(pro_int)
#             self.protein_intake.append(pro_int)
#         elif re.match(self.tdee_re,data) != None:
#             node = self.day_nodes.get(self.current_date.toordinal(),day_node(datetime.date(1000,01,01))) #01/01/1000 denotes an error
#             tdee_ = int(re.split(self.tdee_re,re.split("kcal",data)[0])[1])#Match pattern, split away extraneous stuff
#             node.set_tdee(tdee_)
#             node.set_fic(re.search(self.fic_re,data[-2::]).group())     #Pulls out the endmost non-whitespace character(s)
#             self.tdee.append(tdee_)
#
#     def get_calorie_intake(self):
#         return self.calorie_intake
#     def get_protein_intake(self):
#         return self.protein_intake
#     def get_tdee(self):
#         return self.tdee
#     def get_nodes(self):
#         print "VD" + str(type(self.day_nodes))
#         return self.day_nodes
