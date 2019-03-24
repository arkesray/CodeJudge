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

from models import users, posts, db
from helpers import login_required, allowed_file, submitAnswer, NUMBER_OF_PROBLEMS


#globals
post_number = 1

#database creation
db.create_all()

#using Session for each user
Session(app)


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
            return redirect(url_for('start'))
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
        u = users(request.form.get("name"), request.form.get("roll"),request.form.get("email"), request.form.get("username"), hash, 0, 0)
        db.session.add(u)
        try:
            db.session.commit()
        except:
            return render_template("error.html", title = "error", message = "Username exist! or Something went Wrong.. Can't add you to database! ")
        
        # loging in the user
        session["user_id"] = u.id

        # redirect user to start page
        return redirect(url_for("start"))

    else:
        return render_template( 'register.html', title='Sign Up', year= datetime.datetime.now().year)

  

@app.route('/start',  methods = ["GET","POST"])
@login_required
def start():
    """Renders the home page."""
    userid = session["user_id"]
    user = users.query.filter_by(id = userid).first()
    if user.started != 0:
        return redirect(url_for('profile'))
    elif request.method == "POST":
        v = request.form.get("go") 
        if v == "start":
            user = users.query.filter_by(id = userid).update(dict(started = 1, timeStarted = datetime.datetime.now()))
            try:
                db.session.commit()
            except:
                return render_template("error.html", title = "error", message = "Something went wrong!\n in Database")
            return redirect(url_for('profile'))
    else:
        return render_template('start.html', title='Home Page', year = datetime.datetime.now().year)

@app.route('/profile')
@login_required
def profile():

    uid = session['user_id']
    user = users.query.filter_by(id = uid).first()
    if user.started == 0:
        return redirect(url_for('start'))
    timeRemaining = user.timeAlloted - int((datetime.datetime.now() - user.timeStarted).total_seconds())
    if timeRemaining < 1:
        flash("Timer Ended !! ")
        return redirect(url_for('logout'))
    return render_template('profile.html', name = user.name, title = user.name, problems = NUMBER_OF_PROBLEMS, time = timeRemaining*1000)


@app.route('/profile/submissions')
@login_required
def submissions():
    
    uid = session["user_id"]
    user = users.query.filter_by(id = uid).first()
    post_s = posts.query.filter_by(user_id = uid).order_by(posts.ptime.desc()).all()
    
    if user.started == 0:
        return redirect(url_for('start'))
    
    timeRemaining = user.timeAlloted - int((datetime.datetime.now() - user.timeStarted).total_seconds())
    if timeRemaining < 1:
        flash("Timer Ended !! ")
        return redirect(url_for('logout'))

    return render_template('submissions.html', title = "Status", message = post_s, year= datetime.datetime.now().year)


@app.route('/profile/score')
@login_required
def score():
    """Renders the about page."""
    scoreBoard = users.query.order_by(users.score.desc()).all()
    return render_template( 'score.html', title='Leaderboard', year= datetime.datetime.now().year, lists = scoreBoard)


@app.route('/profile/upload', methods=["POST", "GET"])
@login_required
def upload():
    global post_number

    uid = session["user_id"]
    user = users.query.filter_by(id = uid).first()
    if user.started == 0:
        return redirect(url_for('start'))
    
    timeRemaining = user.timeAlloted - int((datetime.datetime.now() - user.timeStarted).total_seconds())
    if timeRemaining < 1:
        flash("Timer Ended !! ")
        return redirect(url_for('logout'))
    
    elif request.method == "POST":
        lang = request.form.get("lang")
        prbid = int(request.form.get("prbid"))
        
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
                uniqueSubmissionId = "u" + str(uid) + "pn" + str(post_number) + "solToPrb" + str(prbid) + "_"
                filename1 = uniqueSubmissionId + secure_filename(file.filename)
                path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
                file.save(path1)
            else:
                 return render_template("error.html", title = "error", message = "File extension not matched")

        post_number += 1

        p = posts(prbid, filename1, lang, "pending", uid)
        db.session.add(p)
        try:
            db.session.commit()
        except:
            return render_template("error.html", title = "error", message = "Something went wrong!\n in Database")

        t = threading.Thread(target = submitAnswer, args = [p.pid, file.filename.split(".")[0], str(uid), str(prbid), lang, path1])
        t.setDaemon(False)
        t.start()

        # redirect user to profile page
        return redirect(url_for("submissions"))
    else:
        return render_template( 'upload.html', title='Upload', problems = NUMBER_OF_PROBLEMS, year = datetime.datetime.now().year)


@app.route('/error')
@login_required
def error():

    return render_template("error.html")


@app.route('/profile/p/<int:number>')
@login_required
def p(number):
    if number > NUMBER_OF_PROBLEMS:
        return render_template("error.html", title = "error", message = "Problem doesn't exist")
        
    page = "p" + str(number) + ".html"

    return render_template(page, title = "Problem " + str(number))


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
