from data.mod import db_session, users_api
from flask import Flask
import os

app = Flask(__name__, template_folder='templates')
app.debug = True


def main():
    db_session.global_init("data/db/smarty.db")
    app.register_blueprint(users_api.blueprint)
    app.run()


main()
