# -*- coding: utf-8 -*-
import psycopg2
import time
import datetime
import decimal
from decimal import Decimal
from datetime import date
from psycopg2 import Error
from flask import render_template, flash, redirect, url_for, request
from app import app
from flask_login import LoginManager, UserMixin, logout_user, login_required, login_user, current_user
from app.forms import LoginForm, RegisterForm, InfoForm, RateForm
from werkzeug.security import generate_password_hash, check_password_hash
try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user="postgres",
                                  # пароль, который указали при установке PostgreSQL
                                  password="1",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="performance")
except:
    print("Ошибка при работе с PostgreSQL")
    
cursor = connection.cursor()
class User(UserMixin):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return "%d" % (self.id)
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
	return None
login_manager.init_app(app)
login_manager.login_view = "login"
@app.route('/index')
def index():
    if(current_user.is_authenticated):
        cursor.execute('SELECT * FROM public.user where id_user=\'{id_user}\''.format(id_user=current_user.id))
        dd=cursor.fetchone()
        user = {'username': dd[0]}
    else:
        user = {'username':'stranger'}
    return render_template('index.html', title='Home', user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        try:
            username = request.form['username']
            passw = request.form['passw']
            cursor.execute('SELECT * FROM public.user where nickname=\'{nickname}\''.format(nickname=username))
            user=cursor.fetchone()
            if(user==None):
                flash('Неправильно введены данные, повторите попытку.')
            else:
                if(check_password_hash(user[1], passw)==True):
                    id=user[5]
                    user = User(id)
                    login_user(user)
                    if(current_user.is_authenticated):
                        return redirect(url_for('index'))
                else:
                    flash('Неправильно введены данные, повторите попытку.')
        except:
            flash('Неправильно введены данные, повторите попытку.')
    return render_template('Login.html', title='Sign In', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    error=0
    if(current_user.is_authenticated):
        return redirect(url_for('index'))
    form = RegisterForm()
    if request.method == 'POST':
        try:
            username = request.form['username']
            passw = request.form['passw']
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            birthday = request.form['birthday']
            info = request.form['info']
            cursor.execute('SELECT nickname FROM public.user WHERE nickname=\'{nickname}\''.format(nickname=username))
            if(cursor.fetchone()==None):
                cursor.execute('Select Max(id_user) from public.user')
                id_user=cursor.fetchone()[0]+1 #Id для нового пользователя
                try:
                    passw=generate_password_hash(passw, "sha256")
                    cursor.execute('INSERT INTO public.user(nickname, passw, first_name, second_name, birthday, id_user, info) VALUES (\'{nickname}\',\'{passw}\',\'{first_name}\',\'{second_name}\',\'{birthday}\', \'{id_user}\', \'{info}\')'.format(nickname=username, passw=passw, first_name=first_name, second_name=second_name, birthday=birthday, id_user = id_user, info = info))            
                    connection.commit()
                    return redirect(url_for('login'))
                except Exception:
                    flash('Ошибка, неправильно введены данные')
            else:
                flash('Имя пользователя уже занято')
        except:
            flash('Ошибка, не правильно введены данные')
    return render_template('register.html', error=error, form=form)

@app.route('/show/<show>', methods=['GET','POST'])
def show(show):
    rate = 0
    cursor.execute('SELECT show_name FROM public.show where show_name=\'{show}\''.format(show=show))
    name = cursor.fetchone()[0]
    cursor.execute('SELECT id_author FROM public.show where show_name=\'{show}\''.format(show=show))
    id_author = cursor.fetchone()[0]
    cursor.execute('SELECT first_name, second_name FROM public.show NATURAL JOIN public.author WHERE id_author=\'{id_author}\''.format(id_author=id_author))
    author = cursor.fetchone()
    cursor.execute('SELECT id_theatre FROM public.show where show_name=\'{show}\''.format(show=show))
    id_theatre = cursor.fetchone()[0]
    cursor.execute('SELECT theatre_name, address FROM public.show NATURAL JOIN public.theatre WHERE id_theatre=\'{id_theatre}\''.format(id_theatre=id_theatre))
    theatre = cursor.fetchone()
    cursor.execute('SELECT id_show FROM public.show where show_name=\'{show}\''.format(show=show))
    id_show = cursor.fetchone()[0]
    cursor.execute('SELECT role_name, first_name, second_name FROM public.show INNER JOIN public.role ON public.show.id_show = public.role.id_show INNER JOIN actor_role ON public.role.id_role = public.actor_role.id_role INNER JOIN actor ON public.actor_role.id_actor = public.actor.id_actor WHERE public.show.id_show=\'{id_show}\''.format(id_show=id_show))
    roles = cursor.fetchall()
    cursor.execute('SELECT AVG(value) FROM public.rate WHERE id_show=\'{id_show}\''.format(id_show=id_show))
    point=cursor.fetchone()[0]
    if(point!=None):
        rate=point.quantize(Decimal("1.00"), decimal.ROUND_HALF_EVEN)
    cursor.execute('SELECT nickname, value, text, time FROM public.rate WHERE id_show=\'{id_show}\''.format(id_show=id_show))
    texts=cursor.fetchall()   
    form = RateForm()
    if request.method == 'POST':
        try:
            cursor.execute('SELECT * FROM public.user where id_user=\'{id_user}\''.format(id_user=current_user.id))
            nickname = cursor.fetchone()[0]
            cursor.execute('SELECT * FROM public.show where show_name=\'{name}\''.format(name=show))
            id_show = cursor.fetchone()[0]
            value = request.form['value']
            review = request.form['review']
            time = datetime.datetime.now()
            cursor.execute('DELETE FROM public.rate WHERE id_show=\'{id_show}\' AND id_user=\'{id_user}\''.format(id_show=id_show, id_user=current_user.id))
            connection.commit()
            cursor.execute('INSERT INTO public.rate(nickname, id_show, value, text, id_user, time) VALUES (\'{nickname}\', \'{id_show}\', \'{value}\', \'{text}\', \'{id_user}\',\'{time}\' )'.format(nickname = nickname, id_show = id_show, value = value, text = review, id_user=current_user.id, time = time))            
            connection.commit()
        except:
            connection.rollback()
    return render_template('show.html',show=show, name=name, author=author, theatre=theatre, roles=roles, rate=rate, texts=texts, form=form)

@app.route('/user/<username>', methods=["GET", "POST"])
def user(username):
    cursor.execute('SELECT * FROM public.user where id_user=\'{id_user}\''.format(id_user=current_user.id))
    user=cursor.fetchone()[0]
    cursor.execute('SELECT * FROM public.user where id_user=\'{id_user}\''.format(id_user=current_user.id))
    about = cursor.fetchone()[6]
    form = InfoForm()
    if request.method == 'POST':
        try:
            info = request.form['info']
            cursor.execute('UPDATE public.user SET info = \'{info}\' WHERE nickname=\'{nickname}\''.format(nickname = user, info = info))            
            connection.commit()    
        except:
            connection.rollback()

    return render_template('user.html', user=user, form=form, about=about)

@app.route("/shows", methods=["GET", "POST"])
def shows():
    cursor.execute('SELECT show_name FROM public.show')
    shows = cursor.fetchall()
    return render_template('shows.html', shows=shows )

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    


    

