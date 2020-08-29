from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/my-link/')
def my_link():
  os.system('python main.py')
  return 'Click.'

if __name__ == '__main__':
  app.run(debug=True)
