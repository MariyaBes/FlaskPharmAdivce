import flask
from flask import Flask, render_template, request, redirect, url_for, session, flash, json
from flask_mysqldb import MySQL, MySQLdb
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


# # КОРЗИНА
# @app.route('/basket', methods=['POST'])
# def basket ():
#     id_product = request.form['id'];
#     title_product = request.form['title'];
#     price = request.form['price'];
#     image = request.form['img'];
#     count = request.form['count'];

#     print (json.dumps({'id': id_product,
#     'title': title_product,
#     'price': price,
#     'image': image,
#     'count': count}))

#     cursor = mysql.connection.cursor()
#     cursor.execute(f'''SELECT * FROM order_cart WHERE title = "{title_product}"
#     AND ID_User = "{session.get('id')}"''')
#     order_bac = cursor.fetchall()
#     mysql.connection.commit()
#     print("SESSION ORDER", order_bac)
#     if order_bac:
#         session['order'] = True
#         # session['id_order'] = order_bac['ID_Order']
#         session['id_prod'] = order_bac['ID_Medication']
#         if request.form.get('product') == session.get('id_prod'):
#             flash("Такой продукт уже есть", category='error')
#             print("EST PRODUCT")
#     cart_sql = f'''INSERT INTO `order_cart` (`Cost`, `title`, `ID_Medication`, `image`, `Count`, `ID_User`) VALUES ('{price}', '{title_product}', '{id_product}', '{image}', '{count}', '{session.get('id')}')'''
#     return execute_query(connect_db, cart_sql)


# # УДАЛЕНИЕ ТОВАРА ИЗ КОРЗИНЫ
# @app.route('/del_item', methods=['POST'])
# def del_item ():
#     id_del = request.form['id_del']
#     print (json.dumps({'id': id_del}))

#     del_sql = f'''DELETE FROM `order_cart` WHERE `ID_Order` = "{id_del}"'''
#     return execute_query(connect_db, del_sql)

        

# # УДАЛЕНИЕ ТОВАРА ИЗ ИЗБРАННОГО
# @app.route('/del_favourite', methods=['POST'])
# def del_favourite ():
#     id_fav_del = request.form['id_fav_del']
#     print (json.dumps({'id_fav': id_fav_del}))
#     del_fav_sql = f'''DELETE FROM `favourite` WHERE `ID_favourite` = "{id_fav_del}"'''
#     return execute_query(connect_db, del_fav_sql)


# # ОПЛАТА
# @app.route('/pay', methods=['GET', 'POST'])
# def pay():
#     name_id_user = session.get('id')

#     basket_sql = f'''SELECT ID_Medication, Cost, title, image, Count, ID_Order
#     from order_cart
#     where ID_User = "{name_id_user}"
#     group by ID_Order'''
#     basket = execute_read_query(connect_db, basket_sql)

#     order_pay = f'''SELECT ID_Order, sum(Cost*Count) as total_cost_count
#     from order_cart
#     where ID_User = "{name_id_user}"'''
#     order = execute_read_query(connect_db, order_pay)

#     get_user_sql = f'''SELECT name
#     from user
#     where id = "{name_id_user}"'''
#     get_user = execute_read_query(connect_db, get_user_sql)

#     adr_sql = f'''SELECT distinct Address
#     from delivery
#     where User_id = "{name_id_user}"'''
#     adr = execute_read_query(connect_db, adr_sql)

#     if request.form.get('clear_order'):
        
#         del_order = f'''DELETE FROM `order_cart` WHERE `ID_Order` IN ('{request.form.get('clear_order')}')'''
#         execute_query(connect_db, del_order)
#         return redirect('/')

#     return render_template('pay.html', order=order, get_user=get_user, adr=adr, basket=basket)


# # ОФОРМЛЕНИЕ ЗАКАЗА
# @app.route('/order-form', methods=['GET', 'POST'])
# def order_modal():
#     order_pay = f'''SELECT ID_Order, sum(Cost*Count) as total_cost_count
#     from order_cart
#     where ID_User = "{session.get('id')}"'''

#     cart_count_sql = f'''SELECT count(ID_Order) as count_cart
#     from order_cart
#     where ID_Medication > 0
#     and ID_User = "{session.get('id')}"'''
#     cart_count = execute_read_query(connect_db, cart_count_sql)

#     order = execute_read_query(connect_db, order_pay)

#     if request.method == "POST":
#         address = request.form.get('address')
#         id_order = request.form.get('id_order')
#         order_type = request.form.get('order-type')
#         paymant = request.form.get('payment-method')

#         write_sql = f'''INSERT INTO `delivery` (`Delivery`, `Order_ID_Order`, `Pl_cost`, `User_id`, `Address`, `Methods_payment`) 
#         VALUES ('{order_type}', '{id_order}', '149', '{session.get('id')}', '{address}', '{paymant}')'''
#         execute_query(connect_db, write_sql)
#         return redirect('/pay')

#     return render_template ('modal.html', order = order, count = cart_count)


# # СТРАНИЦА ИЗБРАННОЕ
# @app.route('/favourite-list', methods=['GET', 'POST'])
# def favourite():

#     basket_sql = f'''SELECT ID_Medication, Cost, title, image, Count, ID_Order
#     from order_cart
#     where ID_User = "{session.get('id')}"
#     group by ID_Order'''
#     basket = execute_read_query(connect_db, basket_sql)
    
#     cart_count_sql = f'''SELECT count(ID_Order) as count_cart
#     from order_cart
#     where ID_Medication > 0
#     and ID_User = "{session.get('id')}"'''
#     cart_count = execute_read_query(connect_db, cart_count_sql)

#     total_cost_count_sql = f'''SELECT sum(Cost*Count) as total_cost_count
#     from order_cart
#     where ID_User = "{session.get('id')}"'''
#     total_cost_count = execute_read_query(connect_db, total_cost_count_sql)

#     fav_count_sql = f'''SELECT count(ID_favourite) as count_cart
#     from favourite
#     where ID_Medication > 0
#     and ID_User = "{session.get('id')}"'''
#     fav_count = execute_read_query(connect_db, fav_count_sql)

#     cart_count_sql = f'''SELECT count(ID_Order) as count_cart
#     from order_cart
#     where ID_Medication > 0
#     and ID_User = "{session.get('id')}"'''
#     cart_count = execute_read_query(connect_db, cart_count_sql)

#     item_fav_sql = f'''SELECT *
#     from favourite
#     where ID_User = "{session.get('id')}"'''
#     item_fav = execute_read_query(connect_db, item_fav_sql)

#     fav_count_sql = f'''SELECT count(ID_favourite) as count_cart
#     from favourite
#     where ID_Medication > 0
#     and ID_User = "{session.get('id')}"'''
#     fav_count = execute_read_query(connect_db, fav_count_sql)

#     return render_template ('favour.html', count = fav_count, cart_count = cart_count, item = item_fav, fav = fav_count, basket = basket, total_cost_count = total_cost_count)


# @app.route('/add_item', methods=['GET', 'POST'])
# def add_item():
#     if request.method == "POST":
#         item_heart = request.form.get('heart')
#         item_status = request.form.get('status')
#         item_title = request.form.get('title')
#         item_storage = request.form.get('storage')
#         item_price = request.form.get('price')
#         item_image = request.form.get('image')
        
#         print(item_heart, item_status, item_title, item_storage, item_price)
#         write_sql = f'''INSERT INTO `favourite` (`title`, `Data_of_storage`, `Status`, `Cost`, `ID_Medication`, `ID_User`, `Image`)
#         VALUES ('{item_title}', '{item_storage}', '{item_status}', '{item_price}', '{item_heart}', '{session.get('id')}', '{item_image}')'''
#         execute_query(connect_db, write_sql)
#         return redirect('/favourite-list')

# # АПТЕЧКА
# @app.route('/medkit', methods=['POST'])
# def medkit():
#     farm_cpec_sql = f'''SELECT *
#     from pharmacist'''
#     farm_spec = execute_read_query(connect_db, farm_cpec_sql)

#     pecept_sql = f'''SELECT *
#     from recipe'''
#     pecept = execute_read_query(connect_db, pecept_sql)

#     get_user_sql = f'''SELECT name
#     from user
#     where id = "{session.get('id')}"'''
#     get_user = execute_read_query(connect_db, get_user_sql)

#     return render_template('medkit.html', farm = farm_spec, pecept = pecept, get_user = get_user)

if __name__ == '__main__':
    app.run(debug=True)
