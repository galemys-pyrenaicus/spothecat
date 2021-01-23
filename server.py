from flask import Flask, render_template, url_for, request, make_response, flash, jsonify
import flask
import flask_login
import wrapper
import os
import sys
import configparser
import hashlib, uuid
import psycopg2
from psycopg2 import sql
import logging

config = configparser.ConfigParser()
config.read('/etc/spothecat/spothecat.conf')
try:
    dbcred = config['DATABASE']
    ffoncred = config['PHONE']
    gmapcred = config['GMAP']
    logs = config['LOGGING']
    srv = config['SERVER']
    logformat = ['%(asctime)s [%(levelname)s] - %(message)s', '%d-%b-%y %H:%M:%S']
    logging.basicConfig(filename=logs['path'], format=logformat[0], level=logs['level'], datefmt=logformat[1])
except:
    print ("Problem with config")
    sys.exit()
def pass_config():
    return [dbcred, ffoncred, gmapcred, logs, srv]

connlocadb = psycopg2.connect(dbname=dbcred['dbname'], user=dbcred['dbuser'], password=dbcred['dbpass'], host=dbcred['dbhost'])

app = Flask(__name__)
pass_config()

try:
    os.remove('/tmp/spot')
except:
    logging.info("Started")

started=False

app = flask.Flask(__name__)
app.secret_key = 'kawasaki'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def get_user(email):
    cursor = connlocadb.cursor()
    cursor.execute("SELECT * FROM users WHERE login='"+email+"'")
    queryres = cursor.fetchone()
    if cursor.rowcount == 0:
        return "NONEXIST"
    else:
        return queryres
def del_user(email):
    cursor = connlocadb.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE login='"+email+"'")
        connlocadb.commit()
        return True
    except:
        return False

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if get_user(email) == "NONEXIST":
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    email = str(email)
    if get_user(email) == "NONEXIST":
        return
    user = User()
    user.id = email
    passhash_db = get_user(email)[1]
    passhash_form = hashlib.sha256(request.form['password'].encode('utf8')).hexdigest()
    user.is_authenticated = passhash_form == passhash_db
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = flask.request.form['email']
    email = str(email)
    passhash_db = get_user(email)[1]
    passhash_form = hashlib.sha256(request.form['password'].encode('utf8')).hexdigest()
    if passhash_form == passhash_db:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))
    return render_template('index.html', stranger=True, srv_port=srv['port'], srv_address=srv['address'], failedlogin=True)

@app.route('/adduser', methods=['GET', 'POST']) #User management page
@flask_login.login_required
def adduser():
    cursor = connlocadb.cursor()
    connlocadb.commit()
    cursor.execute("SELECT * FROM users")
    queryresl = cursor.fetchall()
    if request.method == "POST":
        req = request.form
        adduser_username = req.get('username')
        adduser_pass_hashed = hashlib.sha256(req.get('password').encode('utf8')).hexdigest()
        cursor = connlocadb.cursor()
        query = "INSERT INTO users (login, pass_hash, role, active) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (adduser_username, adduser_pass_hashed, 'admin', 'true'))
        return flask.redirect('/adduser')
    return render_template("access_list.html", users_list=queryresl, user=flask_login.current_user.id, started=started, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/protected')
@flask_login.login_required
def protected():
    return flask.redirect(url_for('userpage'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect('/')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', stranger=True, srv_port=srv['port'], srv_address=srv['address'], failedlogin=False)

@app.route('/spothecat/')
def userpage():
    try:
        f = open('/tmp/spot', "r")
        started=True
    except:
        started=False
    return render_template("userpage.html", user = flask_login.current_user.id, started=started, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/map/', methods=['GET', 'POST'])
def mapping():
    try:
        f = open('templates/whereami_map.html', "r")
        address = 'whereami_map.html'
    except:
        address = 'nomap.html'
    response = make_response(render_template(address))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.header = 'no-cache'
    return response

@app.route('/log_page/')
@flask_login.login_required
def log_page():
    return render_template('log_page.html', user = flask_login.current_user.id, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/logs/')
def logs():
    with open("/var/log/spothecat.log", "r") as f:
        content = f.read()
    return render_template("log.html", user = flask_login.current_user.id, content=content, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/runscript', methods=['GET', 'POST'])
def runscript():
    wrapper.start()
    return flask.redirect(url_for('userpage'))

@app.route('/stopscript', methods=['GET', 'POST'])
def stopscript():
    wrapper.stop()
    print (url_for('userpage'))
    return flask.redirect(url_for('userpage'))

@app.route('/deleteuser/<username>')
def deleteuser(username):
    if del_user(username):
        flash('Пользователь удалён')
    else:
        flash('Произошла ошибка при удалении пользователя')
    return flask.redirect('/adduser')

@app.errorhandler(404)
def page_not_found(e):
    return flask.redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
