from flask import Flask, render_template, request, url_for
import route


app = Flask(__name__)

menu = [
    {"name": "Главная", "url": "index"},
    {"name": 'О нас', "url": "about"},
    {"name": "Регистрация", "url": "registration"}
]


num = 0

users = []

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
        print(users)
        print(request.form['username'])

    return render_template('registration.html', title="registration", menu=menu, users=users)

@app.route("/profile/<username>")
def profile(username):
    return f"Имя пользователя: {username}"
    print(url_for())


if __name__ == "__main__":
    app.run(debug=True)