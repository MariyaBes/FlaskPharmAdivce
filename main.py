import os
import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, json
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.utils import secure_filename
from flask_login import LoginManager
import re
import datetime
import MySQLdb.cursors
from passlib.hash import sha256_crypt
from models import execute_read_query, execute_query

pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"

app = Flask(__name__)

app.secret_key = 'YV_JNFVJW&*+96+_ETRBO_HOIQ+!FS'
app.permanent_session_lifetime = datetime.timedelta(seconds=900)

# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
# global COOKIE_TIME_OUT
# COOKIE_TIME_OUT = 60*5

login_manager = LoginManager()
# configure file upload
app.config['UPLOAD_FOLDER'] = 'path/to/uploads/folder'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

mysql = MySQL(app)

def create_connection(host, user, password, db):
    connection = False
    try:
        app.config['MYSQL_HOST'] = host
        app.config['MYSQL_USER'] = user
        app.config['MYSQL_PASSWORD'] = password
        app.config['MYSQL_DB'] = db
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        print("Connection to MySQL DB successful")
        connection = True
        return connection

    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e

connect_db = create_connection('localhost', 'root', 'Hn24g%C+', 'pharmadvice')


# АТОРИЗАЦИЯ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(f'''SELECT * FROM user WHERE email = "{email}"''')
        login_user = cursor.fetchone()
        print(login_user)
        try:
            if sha256_crypt.verify(password, login_user['password']):
                if login_user:
                    session['logged_in'] = True
                    session['id'] = login_user['id']
                    session['email'] = login_user['email']
                    return redirect(url_for('home'))
                # else:
                #     flash('Неправильный email/пароль пользователя!', category='error')
            else:
                flash('Неправильный email/пароль пользователя!', category='error')
        except TypeError as e:
            print(e)
            flash('Пользователь не найдет!', category='error')
    return render_template('login.html')

# ВЫХОД
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

# РЕГИСТРАЦИЯ
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form.get('password2')
        checkbox = request.form.get('checkbox')
        password_hash = sha256_crypt.encrypt(request.form['password'])

        check_sql = f'''select * from user where email = "{email}"'''
        account = execute_read_query(connect_db, check_sql)

        if len(name) < 3:
            flash('Имя не должно быть короче 3 символов.', category='error')
        elif password != password2:
            flash('Пароли не совпадают', category='error')
        elif len(email) < 7:
            flash("Email должен быть длинее 7 символов.", category='error')
        elif re.match(pattern, email) is None:
            flash('Email неверный.', category='error')
        elif len(password) < 7:
            flash('Пароль должен быть не более 8 символов.', category='error')
        elif checkbox is None:
            flash('Условия обязательны', category='error')
        elif name[0].islower():
            flash('Имя и фамилия должны начинаться с заглавных букв.')
        else:
            flash('Аккаунт создан!', category='success')
            write_sql = f'''INSERT INTO `user` ( `name`, `email`, `password`) 
            VALUES ('{name}', '{email}', '{password_hash}')'''
            execute_query(connect_db, write_sql)
            return redirect(url_for('login'))
    return render_template('signup.html')


# ГЛАВНАЯ СТРАНИЦА
@app.route('/', methods=['GET', 'POST'])
def home():
    user_id = session.get('id');

    return render_template('index.html')
# log_in = session.get('logged_in'), card_drug = card_drug, basket = basket, cart_count = cart_count, total_cost_count = total_cost_count, fav = fav_count

# СТРАНИЦА ТОВАРА
@app.route('/pharmacist', methods=['GET', 'POST'])
def list():
    request_sql = f'''SELECT pharmacist_id, full_name, stage, email, raiting, clinic_map, pharm_pic, image
    from image, pharmacist
    where pharmacist.pharmacist_id = image.image_id
    and pharmacist_id = image_image_id'''
    list = execute_read_query(connect_db, request_sql)

    
    return render_template('pharm.html', list=list)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        value = request.form.get('search_query')
        check_sql = f'''SELECT pharmacist_id, full_name, stage, email, raiting, clinic_map, pharm_pic, image 
                        FROM image, pharmacist
                        WHERE pharmacist.pharmacist_id = image.image_id
                        and pharmacist.full_name LIKE '%{value}%' group by pharmacist_id'''
        results = execute_read_query(connect_db, check_sql)
        session['search_pro_count'] = len(results)
        return render_template('search.html', value=value, results=results)
    else:
        return render_template('search.html')

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    user_id = session.get('id');

    user_sql = f'''SELECT id, name, email, image
    from user
    where user.id = {user_id}'''
    user = execute_read_query(connect_db, user_sql)

    request_sql = f'''SELECT pharmacist_id, full_name, stage, email, raiting, clinic_map, pharm_pic, image
    from image, pharmacist
    where pharmacist.pharmacist_id = image.image_id
    and pharmacist_id = image_image_id'''
    list = execute_read_query(connect_db, request_sql)
    session['pharm_count'] = len(list)

    return render_template('profile.html', user=user, list=list)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user_id = session.get('id');

    user_sql = f'''SELECT id, name, email, image, address, phone, birth
    from user
    where user.id = {user_id}'''
    user = execute_read_query(connect_db, user_sql)

    return render_template('edit.html', user=user)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')
    birth = request.form.get('date')
    address = request.form.get('text')

    insert_edit = f'''INSERT INTO `user` (`name`, `phone`, `birth`, `address`) VALUES ('{name}', '{phone}', '{birth}', '{address}')'''
    execute_query(connect_db, insert_edit)

    return redirect(url_for('home'))

@app.route('/portfolio/<int:pharmacist_id>', methods=['GET', 'POST'])
def portfolio(pharmacist_id):
    user_id = session.get('id');

    cart_sql = f'''SELECT pharmacist_id, full_name, stage, email, raiting, clinic_map, pharm_pic, image, descript, contact
    FROM image, pharmacist
    where pharmacist_id = "{pharmacist_id}"
    and pharmacist.pharmacist_id = image.image_id
    '''
    card = execute_read_query(connect_db, cart_sql)

    return render_template('portfolio.html', card=card)

if __name__ == '__main__':
    app.run(debug=True)
