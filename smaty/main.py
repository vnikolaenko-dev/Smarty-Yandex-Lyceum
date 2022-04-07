import sys
sys.path.append('../Lib/site-packages/')

from flask import Flask, render_template, redirect, request, abort, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__, template_folder='templates')
app.debug = True
app.config['SECRET_KEY'] = 'b0-sdb-0sbdfb0-bgf0sb-db0vf'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    return None


@app.route("/")
def index():
    return render_template('Главная.html')


if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1')
