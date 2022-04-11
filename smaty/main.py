import os
from PIL import Image
import PIL
from datetime import datetime, date, time
from flask import Flask, flash, render_template, request, redirect, make_response, session
from flask_login import LoginManager

from data.mod import db_session
from data.mod.users import User
from data.mod.posts import Post
from data.mod.user_event import UE

months = {'01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель', '05': 'Май', '06': 'Июнь',
          '07': 'Июль', '08': 'Август', '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'}

app = Flask(__name__, template_folder='templates')
app.debug = True
app.config['SECRET_KEY'] = 'b0-sdb-0sbdfb0-bgf0sb-db0vf'
app.config['UPLOAD_FOLDER'] = '/static/img/events'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("data/db/smarty.db")


def week_day(year, month):
    d, m, y = 1, int(month), int(year)
    if m == 1 or m == 2:
        y -= 1
    m = m - 2
    if m <= 0:
        m += 12
    c = y // 100
    y = y - c * 100
    d = (d + ((13 * m - 1) // 5) + y + (y // 4 + c // 4 - 2 * c + 777)) % 7
    return d


'''
@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")
'''


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template('Главная.html')


@app.route("/reg")
def registration():
    return render_template('Регистрация.html')


@app.route('/reg', methods=['GET', 'POST'])
def my_form_registration():
    mame = request.form['username']
    email = request.form['email'].lower()
    password = request.form['password']

    db_sess = db_session.create_session()

    if db_sess.query(User).filter(
            User.email == email).first():
        return render_template('Регистрация.html', title='Регистрация',
                               message="Такой пользователь уже есть")
    flag = 0
    try:
        if request.form['org'] == '1':
            flag = 1
    except Exception as e:
        pass
    user = User(
        name=mame,
        email=email,
        password=password,
        org=flag
    )
    db_sess.add(user)
    db_sess.commit()
    try:
        if request.form['remember'] == '1':
            db_sess = db_session.create_session()
            rec = db_sess.query(User).filter(User.email == email, User.password == password).first()
            session['id'] = rec.id
            return redirect('/events')
        else:
            return redirect('/log')
    except Exception as e:
        return redirect('/log')


@app.route('/log')
def login():
    return render_template('Войти.html')


@app.route('/log', methods=['GET', 'POST'])
def my_form_login():
    email = request.form['email'].lower()
    password = request.form['password']

    db_sess = db_session.create_session()
    rec = db_sess.query(User).filter(User.email == email, User.password == password).first()

    if rec:
        session['id'] = rec.id
        return redirect('/events')
    else:
        return "Неверный указана почта или пароль"


@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == "POST":
        d = request.form['direction']
        level = request.form['level']
        # Получаем user_id из сессии
        try:
            user_id = session.get('id')
        except Exception as e:
            return redirect('/login')

        db_sess = db_session.create_session()
        a = list(db_sess.query(Post).all())

        b = []
        if db_sess.query(UE).filter(UE.user_id == user_id).first():
            already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')
            for i in a:
                if i.name in already_added and i.public and (i.direc == d or d == '0') \
                        and (i.level == level or level == '0'):
                    b.append([i, True])
                elif i.public and (i.direc == d or d == '0') and (i.level == level or level == '0'):
                    b.append([i, False])
        else:
            for i in a:
                if i.public and (i.direc == d or d == '0') and (i.level == level or level == '0'):
                    b.append([i, False])

        date = str(datetime.now()).split()

        return render_template('Мероприятия.html', owner=False, posts=b, m=int(date[0].split('-')[1]))
    else:
        # Получаем user_id из сессии
        try:
            user_id = session.get('id')
        except Exception as e:
            return redirect('/login')

        db_sess = db_session.create_session()
        a = list(db_sess.query(Post).all())

        b = []
        if db_sess.query(UE).filter(UE.user_id == user_id).first():
            already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')
            for i in a:
                if i.name in already_added and i.public:
                    b.append([i, True])
                elif i.public:
                    b.append([i, False])
        else:
            for i in a:
                if i.public:
                    b.append([i, False])

        date = str(datetime.now()).split()

        return render_template('Мероприятия.html', owner=False, posts=b, m=int(date[0].split('-')[1]))


@app.route('/event/<event_id>')
def event(event_id):
    date = str(datetime.now()).split()

    user_id = session.get('id', 0)
    db_sess = db_session.create_session()
    a = db_sess.query(Post).filter(Post.id == event_id).first()

    flag = 'False'
    if db_sess.query(UE).filter(UE.user_id == user_id).first():
        already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')
        if a.name in already_added:
            flag = 'True'
        try:
            if str(a.id) in db_sess.query(UE).filter(UE.user_id == user_id).first().created.split(','):
                flag = 'CR'
        except Exception as e:
            pass

    try:
        open('static/img/events/' + str(a.id) + '.png')
        flag_photo = True
    except Exception as e:
        flag_photo = False

    db_sess = db_session.create_session()
    a = db_sess.query(Post).filter(Post.id == event_id).first()

    if a.link == '/':
        link_flag = False
    else:
        link_flag = True

    return render_template('Эвент.html', name=a.name,
                           date=str(a.date) + '/' + str(a.month) + '/' + str(a.year), description=a.description,
                           link=a.link, link_flag=link_flag, id=event_id, flag=flag, flag_photo=flag_photo, m=int(date[0].split('-')[1]))


@app.route('/addevent/<event_id>')
def add_event(event_id):
    # Получаем user_id из сессии
    try:
        user_id = session.get('id')
    except Exception as e:
        return redirect('/login')

    db_sess = db_session.create_session()
    event_name = db_sess.query(Post).filter(Post.id == event_id).one().name
    get = db_sess.query(UE).filter(UE.user_id == user_id).first()

    if not (get is None) and not (get.created is None):
        event_line = UE(user_id=user_id,
                        events=get.events + ',' + event_name,
                        created=get.created,
                        public=db_sess.query(User).filter(User.id == user_id).first().org
                        )
        db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
        db_sess.commit()
    else:
        if not (get is None) and get.created is None:
            event_line = UE(user_id=user_id,
                            events=db_sess.query(UE).filter(UE.user_id == user_id).first().events + ',' + event_name,
                            public=db_sess.query(User).filter(User.id == user_id).first().org
                            )
            db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
            db_sess.commit()
        else:
            event_line = UE(user_id=user_id,
                            events=event_name,
                            public=db_sess.query(User).filter(User.id == user_id).first().org
                            )
    db_sess.add(event_line)
    db_sess.commit()

    return redirect('/events')


@app.route('/delevent/<event_id>')
def del_event(event_id):
    # Получаем user_id из сессии
    try:
        user_id = session.get('id')
    except Exception as e:
        return redirect('/login')

    db_sess = db_session.create_session()
    event_name = db_sess.query(Post).filter(Post.id == event_id).one().name

    db_sess = db_session.create_session()
    get = db_sess.query(UE).filter(UE.user_id == user_id).first()
    if not (get is None):
        a = str(get.events).split(',')
        a.remove(event_name)

        v = ','.join(a)

        if not (get.created is None):
            event_line = UE(user_id=user_id,
                            events=v,
                            created=get.created,
                            public=db_sess.query(User).filter(User.id == user_id).first().org)
        else:
            event_line = UE(user_id=user_id,
                            events=v,
                            created=None,
                            public=db_sess.query(User).filter(User.id == user_id).first().org)
        db_sess = db_session.create_session()
        db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
        db_sess.commit()

        db_sess = db_session.create_session()
        if not (get.created is None and len(v) == 0):
            db_sess.add(event_line)
            db_sess.commit()
    else:
        print('Возникла ошибка при удалении ивента')

    return redirect('/events')


@app.route('/calendar/<m>')
def my_calendar(m):
    # Получаем user_id из сессии
    try:
        user_id = session.get('id')
    except Exception as e:
        return redirect('/login')

    date = str(datetime.now()).split()
    year = str(date[0].split('-')[0])

    if int(m) < 10:
        month = '0' + str(m)
    else:
        month = str(m)

    start = week_day(int(year), int(month))
    if start == 0:
        start = 7

    db_sess = db_session.create_session()
    rec = db_sess.query(Post).filter(Post.month == month and Post.year == year).all()

    month = months[month]
    v = []

    already_added = []
    if db_sess.query(UE).filter(UE.user_id == user_id).first():
        already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')

    for i in rec:
        if i.name in already_added:
            v.append([int(i.date), i.id])

    days = []
    num_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    for x in range(-start + 2, num_days[int(m) - 1] + 1):
        flag = True
        for i in v:
            if x == i[0]:
                days.append([x, True, i[1]])
                flag = False
                break
        if flag:
            if x < 1:
                days.append(['', False])
            else:
                days.append([x, False])

    return render_template('Календарь.html', year=year, month=month, days=days, events=v, m=int(m))


@app.route('/create', methods=['GET', 'POST'])
def create_event():
    date = str(datetime.now()).split()

    if request.method == "POST":
        name = request.form['name']
        description = request.form['message']

        try:
            link = request.form['link']
            direc = request.form['direction']
            level = request.form['level']
        except:
            link = '/'
            direc = '0'
            level = '0'

        date = request.form['date']

        d = str(date).split('-')[2]
        m = str(date).split('-')[1]
        y = str(date).split('-')[0]

        user_id = session.get('id')
        db_sess = db_session.create_session()
        post = Post(
            name=name,
            description=description,
            link=link,
            date=d,
            month=m,
            year=y,
            public=db_sess.query(User).filter(User.id == user_id).first().org,
            direc=direc,
            level=level
        )
        db_sess = db_session.create_session()
        db_sess.add(post)
        db_sess.commit()

        db_sess = db_session.create_session()
        get = db_sess.query(UE).filter(UE.user_id == user_id).first()
        if not (get is None) and not (get.created is None):
            a = get.events.split(',')
            a.append(name)
            event_line = UE(user_id=user_id,
                            events=','.join(a),
                            created=get.created + ',' + str(db_sess.query(Post).filter(Post.name == name).first().id),
                            public=db_sess.query(User).filter(User.id == user_id).first().org)
            db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
            db_sess.commit()
        else:
            if not (get is None) and get.created is None:
                event_line = UE(user_id=user_id,
                                events=db_sess.query(UE).filter(UE.user_id == user_id).first().events + ',' + name,
                                created=db_sess.query(Post).filter(Post.name == name).first().id,
                                public=db_sess.query(User).filter(User.id == user_id).first().org
                                )
                db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
                db_sess.commit()
            else:
                event_line = UE(user_id=user_id,
                                events=name,
                                created=db_sess.query(Post).filter(Post.name == name).first().id,
                                public=db_sess.query(User).filter(User.id == user_id).first().org
                                )
        db_sess.add(event_line)
        db_sess.commit()

        try:
            file = request.files["file"]
            event_id = str(db_sess.query(Post).filter(Post.name == name).first().id)
            picture = Image.open(file)
            picture.save('static/img/events/' + event_id + '.png')
        except Exception as e:
            print(e)
        return redirect('/myevents/my')
        # return redirect('/event/' + str(db_sess.query(Post).filter(Post.name == name).first().id))

    db_sess = db_session.create_session()
    # print(id)
    rec = db_sess.query(User).filter(User.id == session.get('id')).first().org
    if rec == 1:
        return render_template('Конструктор.html', m=int(date[0].split('-')[1]))
    else:
        return render_template('ПриватныйКонструктор.html', m=int(date[0].split('-')[1]))


@app.route('/myevents/<own>')
def my_events(own):
    # Получаем user_id из сессии
    try:
        user_id = session.get('id')
    except Exception as e:
        return redirect('/login')

    db_sess = db_session.create_session()
    a = list(db_sess.query(Post).all())

    b, o = [], []
    if not (db_sess.query(UE).filter(UE.user_id == user_id).first() is None):
        if not (db_sess.query(UE).filter(UE.user_id == user_id).first().created is None):
            if own == 'all':
                already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')
                already_cr = db_sess.query(UE).filter(UE.user_id == user_id).first().created.split(',')
                for i in a:
                    if str(i.name) in already_added:
                        if str(i.id) in already_cr:
                            b.append([i, True])
                            o.append(True)
                        else:
                            b.append([i, True])
                            o.append(False)
            elif own == 'my':
                already_cr = db_sess.query(UE).filter(UE.user_id == user_id).first().created.split(',')
                for i in a:
                    if str(i.id) in already_cr:
                        b.append([i, True])
                        o.append(True)
        else:
            if own == 'all':
                already_added = db_sess.query(UE).filter(UE.user_id == user_id).first().events.split(',')
                for i in a:
                    if str(i.name) in already_added:
                        b.append([i, True])
                        o.append(False)
            elif own == 'my':
                pass

    date = str(datetime.now()).split()

    return render_template('ВсеМероприятия.html',
                           posts=dict(pairs=zip(b, o)), m=int(date[0].split('-')[1]),
                           own=own)


@app.route('/delmyevent/<event_id>')
def del_my_event(event_id):
    # Получаем user_id из сессии
    try:
        user_id = session.get('id')
    except Exception as e:
        return redirect('/login')

    db_sess = db_session.create_session()
    event_name = db_sess.query(Post).filter(Post.id == event_id).first().name

    db_sess = db_session.create_session()
    get = db_sess.query(UE).filter(UE.user_id == user_id).first()
    if not (get is None):
        a = str(get.events).split(',')
        if event_name in a:
            a.remove(event_name)

        b = str(get.created).split(',')
        b.remove(str(event_id))

        v = ','.join(a)
        c = ','.join(b)
        event_line = UE(user_id=user_id,
                        events=v,
                        created=c,
                        public=db_sess.query(User).filter(User.id == user_id).first().org)
        db_sess = db_session.create_session()
        db_sess.delete(db_sess.query(UE).filter(UE.user_id == user_id).first())
        db_sess.commit()

        db_sess = db_session.create_session()
        db_sess.delete(db_sess.query(Post).filter(Post.id == event_id).first())
        db_sess.commit()

        db_sess = db_session.create_session()
        if not (len(c) == 0 and len(v) == 0):
            db_sess.add(event_line)
            db_sess.commit()
    else:
        print('Возникла ошибка при удалении ивента')

    try:
        path = 'static/img/events/' + str(event_id) + '.png'
        os.remove(path)
    except Exception as e:
        # Мероприятие без фото
        pass

    return redirect('/myevents/my')


if __name__ == '__main__':
    # app.run(port=5000, host='127.0.0.1')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
