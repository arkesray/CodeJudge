from functools import wraps
from flask import session, redirect
from models import Judge, Problem, db, posts, users, events
import os, datetime

myPath = os.path.abspath('') + "\\CodeJudge\\"

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


ALLOWED_EXTENSIONS = set([ 'c', 'cpp', 'java', 'py'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#database creation

db.create_all()
print("Database File Location\t:", myPath + "database\\database.db")

eventNames = os.listdir(myPath + "database\\events")
NUMBER_OF_EVENTS = len(eventNames)
problems = []

for i in range(NUMBER_OF_EVENTS):
    """ Getting events info """
    h = open(myPath + "database\\events\\" + eventNames[i] + "\\info\\info.txt", "r")
    h1 = h.read().splitlines()
    h.close()

    nn = len(os.listdir(myPath + "database\\events\\" + eventNames[i] + "\\problems\\" ))
    for j in range(nn):
        prbPath = myPath + "database\\events\\" + eventNames[i] + "\\problems\\" + "p" + str(j+1) +"\\"
        p = Problem(prbPath, i+1, eventNames[i], j+1)
        problems.append((i+1,p))
    
    e = events(eventNames[i], int(h1[0]), datetime.datetime.strptime(h1[2], "%d/%m/%Y %H:%M:%S"), datetime.datetime.strptime(h1[3], "%d/%m/%Y %H:%M:%S"), int(h1[1]), " ".join(h1[4:]),nn)
    db.session.add(e)
    try:
        db.session.commit()
        print("Added new event\t\t:", eventNames[i])
    except:
        print("Can't add new event\t:", eventNames[i])
        db.session.rollback()


def MyInit(self, uid, eid, s, st, score ):
    self.userId = uid
    self.eventId = eid
    self.started = s
    self.startTime = st
    self.score = score

eventTablesNames = {}
allEvents = events.query.all()
for ele in allEvents: 
    N = ele.numberOfProblems
    attr_dict = {'__tablename__': ele.name, 'userId': db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, unique=True), 'eventId': db.Column(db.Integer),
     'started': db.Column(db.Integer), 'startTime': db.Column(db.DateTime), 'score': db.Column(db.Integer), '__init__': MyInit}  
    for n in range(N):
        attr_dict['p' + str(n +1)] = db.Column(db.Integer)
    TEST = type(ele.name, (db.Model,), attr_dict)
    eventTablesNames.update({ ele.eid : TEST })



def getProblemList(eid):
    return [v for v in problems if v[0] == eid]


def isTimeUp(u, e):

    if e.etype == 0:
        timeRemaining = int((e.endTime - datetime.datetime.now()).total_seconds())
    else:
        timeRemaining = e.duration - int((datetime.datetime.now() - u.startTime).total_seconds())
    
    return timeRemaining*1000, False if timeRemaining > 0 else True


def submitAnswer(pid, file_name, uid, eid, prbN, lang, file_path, eventTablesNames):
    """
    A fucntion to invoke compile methods and update Database
    """
    fileLocation = myPath + "database\\events\\" + eventNames[int(eid)-1] + "\\users\\" + uid + "\\" + prbN

    if not os.path.exists(fileLocation):
        os.makedirs(fileLocation)
    
    #copying
    h = open( fileLocation + "\\" + file_name + "." + lang, 'w')
    f = open(file_path, 'r')
    h.write(f.read())
    h.close()
    f.close()
    
    evtProblems = getProblemList(int(eid))
    for i in evtProblems:
        if i[1].problemId == int(prbN):
            prb = i[1]
    
    code = Judge(lang, prb)
    if code.complie( fileLocation, file_name + "." + lang) is True:
        if code.execute( fileLocation, file_name + "." + lang) is True:
            code.check( fileLocation, file_name + "." + lang)
    
    pStatus = str(code.stdout.split("#")[1])
    updateStatus(pid, uid, int(eid), int(prbN), lang, pStatus)
    updateScore(pid, uid, int(eid), int(prbN), lang, pStatus, eventTablesNames)
    return


def updateStatus(pid, uid, eid, prbid, lang, pStatus):
    
    p = posts.query.filter_by(pid = pid).update(dict(status = pStatus))   
    try:
        db.session.commit()
    except:
        print("Cannot Update Status in Datebase")

    return


def updateScore(pid, uid, eid, prbid, lang, pStatus, eventTablesNames):
    """
    Updates the database according to the score
    """
    # update score for a problem
    eventPost = eventTablesNames[eid].query.filter_by(userId = uid).first()
    pScore_old = getattr(eventPost, 'p'+str(prbid))
    pScore = calculateScore(pStatus)
    if pScore_old == None or pScore > pScore_old:
        eventPost = eventTablesNames[eid].query.filter_by(userId = uid).update({"p" + str(prbid) : pScore})
        try:
            db.session.commit()
        except:
            print("Cannot Update Score in Datebase")


    ### update total score
    eventPost = eventTablesNames[eid].query.filter_by(userId = uid).first()
    N = events.query.filter_by(eid = eid).first().numberOfProblems
    pScores = [0]*N
    for i in range(N):
        ps = getattr(eventPost, 'p'+str(i+1))
        if ps == None:
            pScores.append(0)
        else:
            pScores.append(ps)
    
    score_old = getattr(eventPost, 'score')
    if score_old == None or sum(pScores) > score_old:
        eventPost = eventTablesNames[eid].query.filter_by(userId = uid).update({"score" : sum(pScores)})
        try:
            db.session.commit()
        except:
            print("Cannot Update Score in Datebase")

    return


def calculateScore(pStatus):
    """
    A fucntion to calculate Score for a particualr submission for a problem
    Implement partial marking here!!!
    """
    if pStatus == "CorrectAnswer":
        return 100
    else:
        return 0

