from functools import wraps
from flask import Flask, render_template, session, request, redirect, url_for
from flask_pymongo import PyMongo
from passlib.hash import pbkdf2_sha256
import os
from os import path
if path.exists("env.py"):
    import env 

app = Flask(__name__)

app.config['MONGO_DBNAME'] = "msproject"
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.secret_key = "B,t=u0W};gBf{DnBClV8/BwiW[1k~7EEzoiv(1Ng'*1k!^R,4sd|4-[:8:_t4c8"
mongo = PyMongo(app)

def check_logged_in(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if 'logged-in' in session:
            return(func(*args, **kwargs))
        else:
            return render_template('nologin.html')
    return wrapped_function

@app.route('/')
@check_logged_in
def home():
    # if session['usertype'] == admin: return admin panel, job posting page
    # else return basic page, job application page, etc
    return render_template('topsecret.html', user_type=session['usertype'])

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        username = request.form['userid']
        password = request.form['password']
        user_type = request.form['type']
        _hash = pbkdf2_sha256.hash(password)
        mongo.db.users.insert_one({
            'username': username,
            'password': _hash,
            'type': user_type
        })
        return redirect(url_for('login'))
        

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['userid']
        user = mongo.db.users.find_one({'username': username})
        user_password = user['password']
        form_password = request.form['password']
        if pbkdf2_sha256.verify(form_password, user_password):
            session['logged-in'] = True
            session['user-id'] = username
            session['usertype'] = user['type']
        else:
            return "login error"    
        return render_template('login.html')

@app.route('/logout')
@check_logged_in
def logout():
    session.pop('logged-in', None)
    session.pop('user-id', None)
    session.pop('usertype', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)