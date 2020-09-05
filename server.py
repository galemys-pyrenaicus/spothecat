from flask import Flask, render_template
from flask import jsonify
import wrapper

import os
user = 'desman'
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html', user=user)

@app.route('/start/')
def result():
  return wrapper.testfunc()

@app.route('/spothecat/'+user+'/')
def userpage():
    return render_template("userpage.html", user=user)

@app.route('/stranger/')
def stangerpage():
    return render_template("index.html", stranger=True)

@app.route('/'+user+'/map/')
def mapping():
    return render_template('whereami_map.html', user=user)

@app.route('/' + user + '/log_page/')
def log_page():
    return render_template('log_page.html', user=user)

@app.route('/logs/')
def logs():
    with open("/var/log/spothecat.log", "r") as f:
        content = f.read()
    return render_template("log.html", content=content)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
