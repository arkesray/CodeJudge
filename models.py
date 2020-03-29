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
    eid = db.Column(db.Integer)
    prbid = db.Column(db.Integer)
    location = db.Column(db.String(200))
    lang = db.Column(db.String(10))
    status = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id') )

    def __init__(self, eid, prbid, l, lang, s = "success", user_id = 0):
        self.ptime = datetime.datetime.now()
        self.eid = eid
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
    post = db.relationship('posts', backref='user', lazy=True)
    
    def __init__(self, name, roll, email, username, password):
        self.name = name
        self.roll = roll
        self.email = email
        self.username = username
        self.password = password



class events(db.Model):
    eid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40), unique = True)
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    description = db.Column(db.String(200))
    numberOfProblems = db.Column(db.Integer)
    
    def __init__(self, name, st, et=datetime.datetime(2020,12,1), desc="This is a contest", N=0):
        self.name=name
        self.startTime=st
        self.endTime = et
        self.description=desc
        self.numberOfProblems=N



class Problem:

    def __init__(self, path, cid, ename, pid):
        self.path = path
        self.contestId = cid
        self.eventName = ename
        self.problemId = pid
        self.TLE = {}
        self.problemSamples = []
        self.problemStatement = []
        self.fetch(self.path)
    
    def extractSampleIO(self, samples):
        i, o = [], []
        gg = i
        for l in samples:
            if l == "----":
                self.problemSamples.append((i,o)) 
                i, o, gg = [], [], i
                continue
            if l == "--":
                gg = o
                continue
            gg.append(l)
        

    def fetch(self, path):
        h = open(path + "web\\all.txt", "r")
        h1 = h.read().splitlines()
        
        self.problemTitle = h1[0]
        self.score = h1[1]
        
        i = 3
        while h1[i] != "":
            self.problemStatement.append(h1[i])
            i += 1 
        i += 1
        self.problemConstrains = []
        while h1[i] != "":
            self.problemConstrains.append(h1[i])
            i += 1
        i += 1
        
        samples = []
        while h1[i] != "":
            samples.append(h1[i])
            i += 1
        i += 1
        self.extractSampleIO(samples)
        while h1[i] != "":
            self.info = h1[i]
            i += 1
        i += 1
        
        while h1[i] != "":
            s = h1[i].split(" ")
            self.TLE[s[0]] = int(s[1])
            i += 1
        i += 1
        
        h.close()
        self.testCases = 1
        
      
class Judge:
    """docstring for compiler"""
    def __init__(self, lang, problem):
        self.lang = lang
        self.prbN = str(problem.problemId)
        self.prbPath = problem.path
        self.runTime = problem.TLE[lang]
        self.stdout = ""
        self.errorCompilation = True
        self.errorTLE = True
        self.errorRTE = True
        self.errorWA = True
        self.CA = False

    
    def complie(self, filelocation, filename):
        """
        Compiles the code
        TODO: different invokes for partial scoring
        """
        compilingCmd = myPath + "static\\batch\\" + self.lang + "c.bat" + " " + self.prbPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]

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
        
        executeCmd = myPath + "static\\batch\\" + self.lang + ".bat" + " " + self.prbPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]
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
        checkCmd = myPath + "static\\batch\\" + "check.bat" + " " + self.prbPath + " " + filelocation + " " + "p" + self.prbN + " " + filename + " " + filename.split(".")[0]
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

  