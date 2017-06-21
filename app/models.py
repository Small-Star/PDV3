import sys
sys.path.insert(0, './app')

from app import db

#Mood
class Mood(db.Model):
    cr_date = db.Column(db.Date, index=True, unique=True, primary_key=True)
    a_l = db.Column(db.Integer)
    a_u = db.Column(db.Integer)
    a_s = db.Column(db.String(length=1))
    v_l = db.Column(db.Integer)
    v_u = db.Column(db.Integer)
    v_s = db.Column(db.String(length=1))

    a_be = db.Column(db.Integer)
    v_be = db.Column(db.Integer)

    def __init__(self, cr_date, a_l, a_u, a_s, v_l, v_u, v_s):
        self.cr_date = cr_date
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
            return float(u - (u - l)*(5/6))
        if s == 'L':
            return float(u - (u - l)*(1/6))
        if s == 'M' or s == 'N':
            return float(u - (u - l)*.5)
        else:
            return 5



    def __repr__(self):
        return str(self.cr_date) + ":" + str(self.a_l) + ":" + str(self.a_u) + ":" + self.a_s + ":" + str(self.v_l) + ":" + str(self.v_u) + ":" + self.v_s
