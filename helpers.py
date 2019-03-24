from functools import wraps
from flask import session, redirect
from models import Judge, Problem, db, posts, users
import os

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


NUMBER_OF_PROBLEMS = len(os.listdir(myPath + "data\\Problems"))
problems = []
for i in range(NUMBER_OF_PROBLEMS):
    problems.append(Problem(i+1, 100))


def submitAnswer(pid, file_name, uid, prbN, lang, file_path):
    """
    A fucntion to invoke compile methods and update Database
    """
    fileLocation = myPath + "data\\users\\" + uid + "\\" + prbN

    if not os.path.exists(fileLocation):
        os.makedirs( fileLocation)
    
    #copying
    h = open( fileLocation + "\\" + file_name + "." + lang, 'w')
    f = open(file_path, 'r')
    h.write(f.read())
    h.close()
    f.close()
    
    code = Judge(lang, problems[prbN - 1])
    if code.complie( fileLocation, file_name + "." + lang) is True:
        if code.execute( fileLocation, file_name + "." + lang) is True:  #TODO; problem-language-input specific runtime
            code.check( fileLocation, file_name + "." + lang)

    updateScore(pid, uid, int(prbN), lang, str(code.stdout.split("#")[1]))
    return


def updateScore(pid, uid, prbid, lang, pStatus):
    """
    Updates the database according to the score
    """
    p = posts.query.filter_by(pid = pid).update(dict(status = pStatus))
    user = users.query.filter_by(id = uid).first()

    score = calculateScore(pStatus)
    if prbid == 1:
        if user.p1 < score:
            u = users.query.filter_by(id = uid).update(dict(p1 = score))
    elif prbid == 2:
        if user.p2 < score:
            u = users.query.filter_by(id = uid).update(dict(p2 = score))
    elif prbid == 3:
        if user.p3 < score:
            u = users.query.filter_by(id = uid).update(dict(p3 = score))
    elif prbid == 4:
        if user.p4 < score:
            u = users.query.filter_by(id = uid).update(dict(p4 = score))
    elif prbid == 5:
        if user.p5 < score:
            u = users.query.filter_by(id = uid).update(dict(p5 = score))
    else:
        print("ERROR Something Unexpected.")

    try:
        db.session.commit()
        score = user.p1 + user.p2 + user.p3 + user.p4 + user.p5
        y = users.query.filter_by(id = uid).update(dict(score = score))
        db.session.commit()
    except:
        print("Cannot Update Status in Datebase")

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