import pymysql
from app import app
from tables import Results
from db_config import mysql
from flask import flash,render_template, request, redirect, url_for, session
import re

@app.route('/home')
def home():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products ")
        rows = cursor.fetchall()
        table = Results(rows)
        table.border = True
        return render_template('home.html', table=table,rows=rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()


@app.route('/buy/<int:id>',methods =['GET'])
def buy_view(id):
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM products ")
        rows = cursor.fetchall()
        if rows:
            return render_template('buy.html', rows=rows ,id=id)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/buy', methods=['POST'])
def buyToCart():
    conn = None
    cursor = None
    try:
        _id = request.form['inputID']
        _product = request.form['inputProduct']
        _amount = request.form['amount[]']
        _price = request.form['price[]']
# validate the received values
        if  _id and _product and _amount and _price and request.method == 'POST':
#do not save password as a plain text
            # _hashed_password = generate_password_hash(_password)
# save edits
            sql = "BEGIN;INSERT INTO order_items( order_id,product_id,amount,price) VALUES(%s,%s,%s,%s);INSERT INTO orders( order_id,user_id,status) VALUES(%s,%s,%s);COMMIT;"
            data = (_id,_product,_amount,_price,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User added successfully!')
            return redirect('/')
        else:
            return 'Error while adding user'
    except Exception as e:
           print(e)
    finally:
           cursor.close() 
           conn.close()

@app.route('/cart',methods =['GET'])
def cart():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM cart JOIN products ON cart.product_id=products.product_id")
        rows = cursor.fetchall()
        # table = Results(rows)
        # table.border = True
        if rows:
            return render_template('cart.html', rows=rows ,id=id)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/cart', methods=['POST'])
def CarttoOrder():
    conn = None
    cursor = None
    try:
        _id = request.form['inputID']
        _product = request.form['inputProduct']
        _amount = request.form['amount[]']
        _price = request.form['price[]']
# validate the received values
        if  _id and _product and _amount and _price and request.method == 'POST':
#do not save password as a plain text
            # _hashed_password = generate_password_hash(_password)
# save edits
            sql = "INSERT INTO order( cart_no) VALUES(%s)"
            data = (_id,_product,_amount,_price,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User added successfully!')
            return redirect('/')
        else:
            return 'Error while adding user'
    except Exception as e:
           print(e)
    finally:
           cursor.close() 
           conn.close()


@app.route('/delete/<int:id>')
def deletes_orders(id):
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE orders_id=%s",(id,))
        conn.commit()
        return redirect('/orders')
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
# log in
@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'user_name' in request.form and 'user_password' in request.form:
		user_name = request.form['user_name']
		user_password = request.form['user_password']
		cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE user_name = % s AND user_password = % s', (user_name, user_password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['user_id'] = account['user_id']
			session['user_name'] = account['user_name']
			msg = 'Logged in successfully !'
			return redirect('/home')
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('user_id', None)
	session.pop('user_name', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'user_password' in request.form and 'user_name' in request.form and 'user_email' in request.form :
		user_name = request.form['user_name']
		user_password = request.form['user_password']
		user_email = request.form['user_email']
		cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE user_ = % s', (user_name, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[A-Za-z0-9]+', user_name):
			msg = 'Username must contain only characters and numbers !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', user_email ):
			msg = 'Invalid email address !'
		elif not user_name or not user_password or not user_email:
			msg = 'Please fill out the form !'

		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (user_name, user_password, user_email ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

# orders
@app.route('/orders',methods =['GET'])
def orders():
    conn = None
    cursor = None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM orderdb.order_items JOIN orderdb.products ON orderdb.order_items.product_id = orderdb.products.product_id JOIN orderdb.orders ON orderdb.order_items.order_id = orderdb.orders.order_id JOIN orderdb.users ON orderdb.orders.user_id = orderdb.users.user_id")
        rows = cursor.fetchall()
        table = Results(rows)
        table.border = True
        if rows:
            return render_template('orders.html', rows=rows)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
