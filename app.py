from flask import Flask, render_template, request, session, url_for, flash, redirect, abort
import route


app = Flask(__name__)

app.config['SECRET_KEY'] = '12341'

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
    return render_template('index.html', title="test", menu=menu, num = num)


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

if __name__ == "__main__":
    app.run(debug=True)