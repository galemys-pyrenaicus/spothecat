from flask import Flask, render_template, url_for, request, make_response
from flask import jsonify
import flask
import flask_login
import wrapper
import os
import configparser

config = configparser.ConfigParser()
config.read('/etc/spothecat/spothecat.conf')
srv = config['SERVER']

app = Flask(__name__)
user='desman'

try:
    os.remove('/tmp/spot')
except:
    print("Token absent")

started=False

app = flask.Flask(__name__)
app.secret_key = 'kawasaki'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {'desman': {'password': ''}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    user.is_authenticated = request.form['password'] == users[email]['password']
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
    if flask.request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'


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
    return flask.redirect(url_for('index', fuckoff=True))

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', stranger=True)

@app.route('/spothecat/'+user+'/')
def userpage():
    try:
        f = open('/tmp/spot', "r")
        started=True
    except:
        started=False
    return render_template("userpage.html", user=flask_login.current_user.id, started=started, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/'+user+'/map/', methods=['GET', 'POST'])
def mapping():
    try:
        f = open('templates/whereami_map.html', "r")
        address = 'whereami_map.html'
    except:
        address = 'nomap.html'
    response = make_response(render_template(address, user=flask_login.current_user.id))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.header = 'no-cache'
    return response

@app.route('/' + user + '/log_page/')
def log_page():
    return render_template('log_page.html', user=flask_login.current_user.id, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/logs/')
def logs():
    with open("/var/log/spothecat.log", "r") as f:
        content = f.read()
    return render_template("log.html", content=content, srv_port=srv['port'], srv_address=srv['address'])

@app.route('/runscript', methods=['GET', 'POST'])
def runscript():
    wrapper.start()
    return flask.redirect(url_for('userpage'))

@app.route('/stopscript', methods=['GET', 'POST'])
def stopscript():
    wrapper.stop()
    print (url_for('userpage'))
    return flask.redirect(url_for('userpage'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
