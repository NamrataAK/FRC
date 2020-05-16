import sqlite3 
from flask import Flask ,flash,session,render_template,redirect,escape, url_for,request, send_from_directory
import sys
import cgi, os
import cgitb; cgitb.enable()
#from werkzeug import secure_filename
import time
import collections



app = Flask(__name__)
app.secret_key = 'any random string'

#homepage
@app.route('/')
def homepage():
	if session:
		session.pop('username', None)					#used to logout of current session
	return render_template('homepage.html')


#page for displaying login for customers
@app.route('/customer')
def customer():
	conn=sqlite3.connect('members.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM customers")
	var=cur.fetchall()
	conn.close()
	return render_template('customer.html',var=var)
	#from customer.html , goes to homepage_customer()

#customer session is created after log in
@app.route('/customer_logged_in',methods=['GET','POST'])
def customer_logged_in():
	session['username']=request.form['username']              #session is a dictionery with username its key.. value is nm variable
	return redirect(url_for('homepage_customer'))

#customer session created after sign up
@app.route('/customer_signed_up',methods=['GET','POST'])
def customer_signed_up():
	session['username']=request.form['username']             #session is a dictionery with username its key.. value is nm variable
	password=request.form['password']
	conn=sqlite3.connect('members.db')
	cur=conn.cursor()
	cur.execute("INSERT INTO customers(username,password) VALUES (?,?)",(session['username'],password))
	cur.execute("CREATE TABLE {}(item text NOT NULL ,price INTEGER , qty TEXT ,total INTEGER , place TEXT ,rest TEXT,dish_image TEXT)".format(session['username']))
	temp=session['username']+'_orders'
	cur.execute("CREATE TABLE IF NOT EXISTS {}(item text NOT NULL ,price INTEGER , qty TEXT ,total INTEGER , place TEXT ,rest TEXT,dish_image TEXT);".format(temp))
	conn.commit()
	return redirect(url_for('homepage_customer'))


#when customer wants to logout
@app.route('/customer_logout')
def customer_logout():
	session.pop('username', None)					#used to logout of current session
	return redirect(url_for('homepage'))




#homepage of customer where restaurants are needed to be selected
@app.route('/homepage_customer')
def homepage_customer():
	conn=sqlite3.connect('members.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM response WHERE username=?",(session['username'],))
	response=cur.fetchall()
	cur.execute("SELECT * FROM most_ordered ORDER BY orders DESC limit 4")
	most_ordered=cur.fetchall()
	conn.close()
	return render_template('homepage_customer.html',response=response,most_ordered=most_ordered)



#to show items in cart
@app.route('/liked')
def liked():
	return render_template('liked.html')

@app.route('/purchased')
def purchased():
	return render_template('purchased.html')

@app.route('/search')    
def search():
	return render_template('search.html')
			



if __name__ == '__main__':
   app.run(debug = True)	

