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
    location = db.Column(db.String(200))
    lang = db.Column(db.String(10))
    status = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id') )

    def __init__(self, prbid, l, lang, s = "success", user_id = 0):
        self.ptime = datetime.datetime.now()
        self.prbid = prbid
        self.location = l
        self.lang = lang
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


class Judge:

    """docstring for compiler"""
    def __init__(self, lang, problem):
        self.lang = lang
        self.prbN = problem.problemId
        self.runTime = getRunTime(prbN, problem)
        self.stdout = ""
        self.errorCompilation = True
        self.errorTLE = True
        self.errorRTE = True
        self.errorWA = True
        self.CA = False
    
    def getRunTime(self, problem):
        if self.lang == "py":
            return problem.pyTLE
        elif self.lang == "java":
            return problem.javaTLE
        elif self.lang == "cpp":
            return problem.cppTLE

    def complie(self, filelocation, filename):
        """
        Compiles the code
        TODO: different invokes for partial scoring
        """
        compilingCmd = myPath + "static\\batch\\" + self.lang + "c.bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]

        if self.lang == "java" or self.lang == "cpp":
            p = subprocess.Popen( compilingCmd, stdout = subprocess.PIPE )
            stdout,stderr = p.communicate()
            self.stdout = stdout.decode("utf-8")
            if self.stdout.split("#")[1] == "CompilationSuccess":
                self.errorCompilation = False
                return True
            else:
                return False
        else:
            self.errorCompilation = False
            return True

    
    def execute(self, filelocation, filename):

        executeCmd = myPath + "static\\batch\\" + self.lang + ".bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]
        if not self.errorCompilation:

            p = subprocess.Popen(executeCmd, stdout = subprocess.PIPE )
            try:
                stdout,stderr = p.communicate(timeout = self.runTime)
                self.stdout = stdout.decode("utf-8")
            except subprocess.TimeoutExpired:
                #p.kill()
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
                self.stdout = "#TimeLimitExceded#"
                return False
        else:
            print("Something Wrong! -c\n")
            return False

        if self.stdout.split("#")[1] != "RunTimeError":
            self.errorRTE = False
        if self.stdout.split("#")[1] != "TimeLimitExceded":
            self.errorTLE = False

        return True


    def check(self, filelocation, filename):
        checkCmd = myPath + "static\\batch\\" + "check.bat" + " " + myPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]
        if not self.errorCompilation and not self.errorTLE and not self.errorRTE:
            p = subprocess.Popen(checkCmd, stdout = subprocess.PIPE )
            stdout,stderr = p.communicate()
            self.stdout = stdout.decode("utf-8")
        else:
            print("Not Checking! Something Wrong!")
            return False

        if self.stdout.split("#")[1] == "CorrectAnswer":
            self.errorWA = False
            self.CA = True

        return True


class Problem:

    def __init__(self, pid, score, pyTLE = 5, cppTLE = 2, javaTLE = 3, TC = 1):
        self.problemId = pid
        self.score = score
        self.pyTLE = pyTLE
        self.cppTLE = cppTLE
        self.javaTLE = javaTLE
        self.testCases = TC
        


