from flask import Flask, render_template
import route


app = Flask(__name__)

menu = ["one", "two", "three"]

num = 0

@app.route("/")
def index():
    return render_template('index.html', title="test", menu=menu, num = num)


@app.route("/about")
def about():
    return "<h1>Hello world</h1>"


if __name__ == "__main__":
    app.run(debug=True)