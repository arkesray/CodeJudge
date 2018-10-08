from CodeJudge import app
from flask_sqlalchemy import SQLAlchemy
import datetime
import subprocess
import os

db = SQLAlchemy(app)
myPath = os.path.abspath('') + "\\CodeJudge\\"


class posts(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    ptime = db.Column(db.DateTime)
    prbid = db.Column(db.Integer)
    sol = db.Column(db.String(200))
    status = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id') )

    def __init__(self, prbid, i1, s = "success", user_id = 0):
        self.ptime = datetime.datetime.now()
        self.prbid = prbid
        self.sol = i1
        self.status = s
        self.user_id = user_id

class users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    roll = db.Column(db.String(20))
    email = db.Column(db.String(20))  
    username = db.Column(db.String(20), unique = True)
    password = db.Column(db.String(513))
    p1 = db.Column(db.Integer)
    p2 = db.Column(db.Integer)
    p3 = db.Column(db.Integer)
    p4 = db.Column(db.Integer)
    p5 = db.Column(db.Integer)
    score = db.Column(db.Integer)
    started = db.Column(db.Integer)
    timeStarted = db.Column(db.DateTime)
    timeAlloted = db.Column(db.Integer)
    post = db.relationship('posts', backref='user', lazy=True)
    
    def __init__(self, name, roll, email, username, password, score, status = 0 ):
        self.name = name
        self.roll = roll
        self.email = email
        self.username = username
        self.password = password
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.p4 = 0
        self.p5 = 0
        self.score = score
        self.started = status
        self.timeStarted = datetime.datetime.now()
        self.timeAlloted = int(datetime.timedelta(hours = 20).total_seconds())



