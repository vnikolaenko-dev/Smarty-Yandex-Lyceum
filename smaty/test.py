from data import db_session, news_api


def main():
    db_session.global_init("data/db/smarty.db")
    app.register_blueprint(news_api.blueprint)
    app.run()

main()