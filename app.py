from cmath import log
from distutils.debug import DEBUG
import re
from flask import Flask, make_response, render_template, request, session, url_for, flash, redirect, abort, g
import sqlite3, os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin


#config
DATABASE = 'tmp/flsite.db'
DEBUG = True
SECRET_KEY = '12341'
MAX_CONTENT_LENGTH = 1024*1024
dbase = None


app = Flask(__name__)
app.config['SECRET_KEY'] = '725a259864a0f8c7636a25ddc63a8c966afd6f86'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для начала работы авторизуйтесь'
login_manager.login_message_category = 'success'

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
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    db = get_db()
    dbase = FDataBase(db)
    print(type(dbase.getMenu()))
    return render_template('index.html', title="test", menu=dbase.getMenu(), num = num, posts=dbase.getPostsAnonce(), visits=session['visits'])


@app.route("/about")
def about():
    return render_template('about.html', title="about", menu=menu)

@app.route("/registration", methods=['POST',"GET"])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash('Вы успешно зарегистрированы', 'success')
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", 'error')

    return render_template('registration.html', title="registration", menu=menu, form=form)

# @app.route("/login", methods=['POST', "GET"])
# def login():
#     if request.method == "POST":
#         if 'userLogged' in session:
#             return redirect(url_for('profile', username=session['userLogged']))
#         elif request.form['username'] == 'islam' and request.form['password'] == '123':
#             session['userLogged'] = request.form['username']
#             return redirect(url_for('profile', username=session['userLogged']))
#     return render_template('login.html', title='Авторизация', menu=menu)

# @app.route("/login")
# def login():
#     log = ""
#     if request.cookies.get('logged'):
#         log = request.cookies.get('logged')
#         print(request.cookies)
    
#     res = make_response(f'<h1>Форма авторизации</h1> <p>logged {log}</p>')
#     res.set_cookie('logged', 'yes', 30*24*3600)
#     return res

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['password'], form.psw.data):
            userLogin = UserLogin().create(user)
            rm = form.remember.data
            print(rm)
            login_user(userLogin, remember=rm)
            return redirect(request.args.get("next") or url_for('profile'))
        flash("Неверная пара логин/пароль", 'error')
    return render_template("login.html", form=form)
    # if request.method == "POST":
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['password'], request.form['password']):
    #         userLogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         print(rm)
    #         login_user(userLogin, remember=rm)
    #         return redirect(request.args.get("next") or url_for('profile'))
    #     flash("Неверная пара логин/пароль", 'error')

    # return render_template('login.html', title='Авторизация')


@app.route("/add_post", methods=["POST","GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            print(res)
            if not res:
                flash("Ошибка добавления статьи", category='error')
                print("ОШИБКА ЗДЕСЬ")
            else:
                flash("Статья добавлена успешно", category='success')
        else:
            flash("Ошибка добавления статьи#2", category='error')
            print(request.form['name'], request.form['post'])
    return render_template('add_post.html', menu=menu, title='Добавление статьи')

@app.route('/post/<alias>', methods=["POST", "GET"])
@login_required
def showPost(alias):
    id_post,title,post,likes = dbase.getPost(alias)
    if request.method == "POST":
        flash("YES")
        request.method = None
    else:
        print("NO")
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post, likes=likes, id_post=id_post)

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


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@login_manager.user_loader
def load_user(user_id):
    print("load user")
    return UserLogin().fromDB(user_id, dbase)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    print("Я ТУТ")
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", 'error')
                flash("Аватар обновлен", 'success')
            except FileNotFoundError as e:
                flash("Ошибка чтения аватара", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for("profile"))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль')

if __name__ == "__main__":
    app.run(debug=True)