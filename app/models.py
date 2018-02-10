import sys
sys.path.insert(0, './app')

from app import db
from config import *

#Main DB
class QS_Params(db.Model):
    __tablename__ = 'qs_params'

    date = db.Column(db.Date, index=True, unique=True, primary_key=True)

    #Diet
    kcal_intake = db.Column(db.Integer)
    intake_error_bar = db.Column(db.Integer)
    protein_intake = db.Column(db.Integer)
    protein_intake_error_bar = db.Column(db.Integer)
    carb_intake = db.Column(db.Integer)
    net_carb_intake = db.Column(db.Integer)
    tdee = db.Column(db.Integer)
    tdee_error_bar = db.Column(db.Integer)
    cycle_phase = db.Column(db.String(length=2))
    cycle_num = db.Column(db.Integer)

    net_intake = db.Column(db.Float)
    fiber_intake = db.Column(db.Float)
    fat_intake = db.Column(db.Float)

    #RHR
    rhr_time = db.Column(db.String(length=5))    #TODO:Parse into datetime
    bpm = db.Column(db.Integer)

    #Other Tables
    mood = db.relationship('Mood', uselist=False, back_populates="qsp", primaryjoin="QS_Params.date == Mood.date")
    journals = db.relationship('Mood', uselist=False, back_populates="qsp", primaryjoin="QS_Params.date == Mood.date")

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date) + ": " + str(self.kcal_intake)

    def compute_derived_vals(self):
        #Derived values
        if (self.tdee == None) or (self.tdee <= 0):  #This day has no TDEE recorded
            self.tdee = None
            self.net_intake = None

        else:
            self.net_intake = self.kcal_intake - self.tdee

        if self.carb_intake > 0:#Assume if carb_intake is present than net_carb_intake will be as well
            self.fiber_intake = self.carb_intake - self.net_carb_intake #An approximation, but...
            self.fat_intake = (self.kcal_intake - self.protein_intake*ACF_P - self.net_carb_intake*ACF_C - self.fiber_intake*ACF_FI)/ACF_F #This limb is very thin...


#Mood
class Mood(db.Model):
    __tablename__ = 'mood'
    date = db.Column(db.Date, db.ForeignKey('qs_params.date'), index=True, unique=True, primary_key=True)
    qsp = db.relationship("QS_Params", back_populates="mood")
    a_l = db.Column(db.Integer)
    a_u = db.Column(db.Integer)
    a_s = db.Column(db.String(length=1))
    v_l = db.Column(db.Integer)
    v_u = db.Column(db.Integer)
    v_s = db.Column(db.String(length=1))

    a_be = db.Column(db.Integer)
    v_be = db.Column(db.Integer)

    def __init__(self, date, a_l, a_u, a_s, v_l, v_u, v_s):
        self.date = date
        self.a_l = a_l
        self.a_u = a_u
        self.a_s = a_s
        self.v_l = v_l
        self.v_u = v_u
        self.v_s = v_s

        #Derived values
        self.a_be = self.lobe(a_l,a_u,a_s)
        self.v_be = self.lobe(v_l,v_u,v_s)

    def lobe(self,l,u,s):
        '''Return single value best estimate'''
        if s == 'U':
            return float(u - (u - l)*(1/6))
        if s == 'L':
            return float(u - (u - l)*(5/6))
        if s == 'M' or s == 'N':
            return float(u - (u - l)*.5)
        else:
            return 5

    def __repr__(self):
        return str(self.date) + ":" + str(self.a_l) + ":" + str(self.a_u) + ":" + self.a_s + ":" + str(self.v_l) + ":" + str(self.v_u) + ":" + self.v_s

# class Journals(db.Model):
#     __tablename__ = 'journals'
#     date = db.Column(db.Date, db.ForeignKey('qs_params.date'), index=True, unique=True, primary_key=True)
#     qsp = db.relationship("QS_Params", back_populates="journals")
