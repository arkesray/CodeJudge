from functools import wraps
from flask import session, redirect
#from models import Compiler
import os

myPath = os.path.abspath('') + "\\CodeJudge\\data\\"

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


