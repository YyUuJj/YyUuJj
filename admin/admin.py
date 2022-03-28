
import re
from turtle import title
from flask import Blueprint, redirect, url_for, render_template, request, flash, session

menu = [{'url': ".index", 'title': 'Панель'},
        {'url': '.logout', 'title': 'Выйти'}]

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)

@admin.route("/")
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title="Админ-панель")

@admin.route('/login', methods=['GET', "POST"])
def login():
    if request.method == "POST":
        if request.form['user'] == 'admin' and request.form['psw'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", 'error')
    return render_template('admin/login.html', title='Админ-панель')

@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    
    logout_admin()

    return redirect(url_for('.login'))