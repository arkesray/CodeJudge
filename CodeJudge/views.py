import os
import string
import datetime
import time
import threading

from flask import render_template, session, redirect, request, url_for, flash
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from CodeJudge import app

from models import users, posts, events, db, Problem
from helpers import login_required, allowed_file, submitAnswer, getProblemList, isTimeUp, eventTablesNames


#globals
post_number = 1

#using Session for each user
Session(app)

"""
    if user.started == 0:
        return redirect(url_for('start'))
    timeRemaining = user.timeAlloted - int((datetime.datetime.now() - user.timeStarted).total_seconds())
    if timeRemaining < 1:
        flash("Timer Ended !! ")
        return redirect(url_for('logout'))
"""

db.create_all()


@app.route('/')
# a simple page that says hello
@app.route('/home')
def home():
    return render_template('home.html', title = 'Home', year=datetime.datetime.now().year)

@app.route('/login', methods = ["GET","POST"])
def login():
    """Renders the login page."""
    if request.method == "POST":
        
        password = request.form.get("pass")
        username = request.form.get("username")
        user = users.query.filter_by(username = username).first()

        if not user:
            return render_template("error.html", title = "error", message = "Incorrect username")

        hash = pwd_context.verify(password, user.password)
        
        if not hash:
            return render_template("error.html", title = "error", message = "Incorrect password")
        else:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
    else:
        return render_template( 'login.html', title = 'Log In', year=datetime.datetime.now().year)


@app.route('/register', methods = ["GET", "POST"])
def register():
    
    if request.method == "POST":
        
        pass1 = request.form.get("pass1")
        pass2 = request.form.get("pass2")

        # ensure both passwords are same
        if pass1 != pass2:
            return render_template("error.html", title = "error", message = "The passwords you entered, Do not match!")

        # to encrypt password
        hash = pwd_context.encrypt(pass1)
        u = users(request.form.get("name"), request.form.get("roll"),request.form.get("email"), request.form.get("username"), hash)
        db.session.add(u)
        #try:
        db.session.commit()
        #except:
            #return render_template("error.html", title = "error", message = "Username exist! or Something went Wrong.. Can't add you to database! ")
        
        # loging in the user
        session["user_id"] = u.id

        # redirect user to start page
        return redirect(url_for('profile'))

    else:
        return render_template( 'register.html', title='Sign Up', year= datetime.datetime.now().year)

  
@app.route('/profile')
@login_required
def profile():

    uid = session['user_id']
    user = users.query.filter_by(id = uid).first()
    eventList = events.query.order_by(events.eid).all()
    return render_template('profile.html', name = user.name, title = user.name, events=eventList)


@app.route('/profile/submissions')
@login_required
def submissions():
    
    uid = session["user_id"]
    user = users.query.filter_by(id = uid).first()
    post_s = posts.query.filter_by(user_id = uid).order_by(posts.ptime.desc()).all()

    return render_template('submissions.html', title = "Status", message = post_s, year= datetime.datetime.now().year)


@app.route('/profile/event/<int:number>', methods = ["GET","POST"])
@login_required
def event(number):

    """Renders the event page."""
    userid = session["user_id"]
    e = events.query.filter_by(eid=number).first()
    timeToStart = (e.startTime - datetime.datetime.now()).total_seconds()
    canStart = False if timeToStart >= 1 else True
    
    if request.method == "POST":
        go = request.form.get("go")

        if go == "register":
            
            u = eventTablesNames[e.eid](userid, number, 0, datetime.datetime.now(), 0)
            db.session.add(u)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
            return redirect(url_for('event', number = number)) 

        if go == "start":
            u = eventTablesNames[e.eid].query.filter_by(userId=userid).update(dict(started=1,startTime = datetime.datetime.now()))
            try:
                db.session.commit()
            except:
                db.session.rollback()
            return redirect(url_for('emain', number = number))

    else:
        u = eventTablesNames[e.eid].query.filter_by(userId=userid).first()
        if u is None:
            return render_template('startLayout.html', reg=False, tts=timeToStart*1000, ct=canStart, title='Event Welcome', year=datetime.datetime.now().year, e=e)
        if u.started == 1:
            return redirect(url_for('emain', number=number))

        return render_template('startLayout.html', reg=True, tts=timeToStart*1000, ct=canStart, title='Event Welcome', year=datetime.datetime.now().year, e=e)


@app.route('/profile/event/<int:number>/emain')
@login_required
def emain(number):
    "The Problem list for each event"
    
    userid = session["user_id"]
    e = events.query.filter_by(eid=number).first()
    u = eventTablesNames[e.eid].query.filter_by(userId=userid).first()

    timeRemaining = isTimeUp(u, e)[0]

    return render_template('emain.html', title='Main Page', num = number, eventName = e.name, timeLeft = timeRemaining, problems = e.numberOfProblems)


@app.route('/profile/event/<int:number>/p/<int:id>')
@login_required
def p(number, id):
    userid = session["user_id"]
    e = events.query.filter_by(eid=number).first()
    u = eventTablesNames[e.eid].query.filter_by(userId=userid).first()

    problems = getProblemList(number)
    for i in problems:
        if i[1].problemId == id:
            prb = i[1]
    
    return render_template('problemLayout.html', title = "Problem " + str(id), P=prb, timeUp = isTimeUp(u, e)[1])


@app.route('/profile/event/<int:number>/score')
@login_required
def score(number):
    """Renders the score page."""
    evt = events.query.filter_by(eid = number).first() 
    t = db.session.query(users.name, eventTablesNames[number]).join(eventTablesNames[number], users.id==eventTablesNames[number].userId).order_by(eventTablesNames[number].score.desc()).all()
    return render_template( 'score.html', title='Leaderboard', year= datetime.datetime.now().year, num=evt.numberOfProblems, lists = t)


@app.route('/profile/upload/<int:number>/p/<int:id>', methods=["POST", "GET"])
@login_required
def upload(number, id):
    global post_number

    uid = session["user_id"]
    evt = events.query.filter_by(eid = number).first()
    u = eventTablesNames[evt.eid].query.filter_by(userId=uid).first()
    timeUp = isTimeUp(u, evt)

    if request.method == "POST":
        lang = request.form.get("lang")
        prbid = int(request.form.get("prbid"))
        eventId = int(request.form.get("eventId"))
        
        # check if the post request has the file part
        if "solution" not in request.files.keys():
            filename1 = "noimage.txt"
            return render_template("error.html", title = "error", message = "File not found")
        else:
            file = request.files['solution']
        # if user does not select file, browser also
        # submit a empty part without filename
            if file.filename == '':
                filename1 = "noimage.txt"
            elif file and allowed_file(file.filename):
                uniqueSubmissionId = "u" + str(uid) + "pn" + str(post_number) + "eid" + str(eventId) + "pid" + str(prbid) + "_"
                filename1 = uniqueSubmissionId + secure_filename(file.filename)
                path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
                file.save(path1)
            else:
                 return render_template("error.html", title = "error", message = "File extension not matched")

        post_number += 1

        if not timeUp[1]:
            p = posts(number, prbid, filename1, lang, "pending", uid)
        else:
            p = posts(number, prbid, filename1, lang, "TimeUp", uid)
        db.session.add(p)
        try:
            db.session.commit()
        except:
            return render_template("error.html", title = "error", message = "Something went wrong!\n in Database")
        
        if not timeUp[1]:
            t = threading.Thread(target = submitAnswer, args = [p.pid, file.filename.split(".")[0], str(uid), str(eventId), str(prbid), lang, path1, eventTablesNames])
            t.setDaemon(False)
            t.start()

        # redirect user to profile page
        return redirect(url_for("submissions"))
    else:
        return render_template( 'upload.html', title='Upload', event=evt, timeUp = timeUp[1], selectedPid=id, year = datetime.datetime.now().year)



@app.route('/error')
@login_required
def error():

    return render_template("error.html")


@app.route("/logout")
def logout():
    """Log user out."""
    for key in list(session):
        if key != '_permanent':
            session.pop(key)
    session['this'] = 'will be added'
    flash("Logged you out!!")
    # forget any user_id
    #session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
