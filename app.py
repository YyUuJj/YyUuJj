from distutils.debug import DEBUG
from flask import Flask, render_template, request, session, url_for, flash, redirect, abort, g
import sqlite3, os
from FDataBase import FDataBase

#config
DATABASE = 'tmp/flsite.db'
DEBUG = True
SECRET_KEY = '12341'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))


menu = [
    {"name": "Главная", "url": "index"},
    {"name": 'О нас', "url": "about"},
    {"name": "Регистрация", "url": "registration"}
]


num = 0

users = []

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu)

@app.route("/")
@app.route("/index")
def index():
    db = get_db()
    dbase = FDataBase(db)
    print(type(dbase.getMenu()))
    return render_template('index.html', title="test", menu=dbase.getMenu(), num = num, posts=dbase.getPostsAnonce())


@app.route("/about")
def about():
    return render_template('about.html', title="about", menu=menu)

@app.route("/registration", methods=['POST',"GET"])
def registration():
    if request.method == "POST":
        users.append(request.form['username'])
        if len(request.form['username']) > 2:
            flash("Сообщение отправлено", category='success')
        else:
            flash("ошибка отправки", category='error')

    return render_template('registration.html', title="registration", menu=menu, users=users)

@app.route("/login", methods=['POST', "GET"])
def login():
    if request.method == "POST":
        if 'userLogged' in session:
            return redirect(url_for('profile', username=session['userLogged']))
        elif request.form['username'] == 'islam' and request.form['password'] == '123':
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html', title='Авторизация', menu=menu)

@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        print("СРАБОТАЛО")
        abort(401)
    return f"Имя пользователя: {username}"


@app.route("/add_post", methods=["POST","GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash("Ошибка добавления статьи", category='error')
                print("ОШИБКА ЗДЕСЬ")
            else:
                flash("Статья добавлена успешно", category='success')
        else:
            flash("Ошибка добавления статьи", category='error')
            print(request.form['name'], request.form['post'])
    return render_template('add_post.html', menu=menu, title='Добавление статьи')

@app.route('/post/<alias>')
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title,post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    else:
        print('бд подключена')
    return g.link_db

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


if __name__ == "__main__":
    app.run(debug=True)