import flask
from . import db_session

from .posts import Post
from .users import User

from flask import jsonify


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    events = db_sess.query(Post).all()
    return jsonify(
        {
            'events':
                [item.to_dict(only=('name', 'description', 'link'))
                 for item in events]
        }
    )


@blueprint.route('/api/post/<id>')
def get_post(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Post).filter(Post.id == id).all()

    try:
        return jsonify(
            {
                id:
                    item.to_dict(only=('name', 'description', 'link'))
                    for item in event
            }
        )
    except AttributeError:
        return "Такого мероприятия не существует"


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    events = db_sess.query(User).all()
    return jsonify(
        {
            'events':
                [item.to_dict(only=('name', 'email'))
                 for item in events]
        }
    )


@blueprint.route('/api/user/<id>')
def get_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).all()

    try:
        return jsonify(
            {
                id:
                    item.to_dict(only=('name', 'email'))
                for item in user
            }
        )
    except AttributeError:
        return "Такого пользовател не существует"


@blueprint.route('/api/add_user/<name>/<email>/<password>')
def add_user(name, email, password):
    db_sess = db_session.create_session()

    if db_sess.query(User).filter(
            User.email == email).first():
        return "Такой пользователь уже есть"
    flag = 0
    user = User(
        name=name,
        email=email,
        org=flag
    )

    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()

    user = db_sess.query(User).filter(User.email == email).all()
    try:
        return jsonify(
            {
                user[0].id:
                    item.to_dict(only=('name', 'email'))
                for item in user
            }
        )
    except AttributeError:
        return "Ошибка при регистрации пользователя"


@blueprint.route('/api/del_user/<email>/<password>')
def del_user(email, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        try:
            db_sess.delete(db_sess.query(User).filter(User.email == email).first())
            db_sess.commit()
            return "Пользователь был успешно удалён"
        except AttributeError:
            return "Ошибка при удалении пользователя"
    else:
        return "Неверная почта или пароль"
