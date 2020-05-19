import sqlite3 
from flask import Flask ,flash,session,render_template,redirect,escape, url_for,request, send_from_directory
import sys
import cgi, os
import cgitb; cgitb.enable()
#from werkzeug import secure_filename
import time
import collections
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
import heapq



app = Flask(__name__)
app.secret_key = 'any random string'

###########################################################################################################

# Data downloaded from https://grouplens.org/datasets/movielens/100k/

#Reading users file:
u_cols = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
users = pd.read_csv('ml-100k/u.user', sep='|', names=u_cols,
 encoding='latin-1')

#Reading ratings file:
r_cols = ['user_id', 'dish_id', 'rating', 'unix_timestamp']
ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=r_cols,
 encoding='latin-1')

#Reading items file:
i_cols = ['Dish id', 'Dish Name', 'Nutrition Value', 'Food Information', 'Unknown', 'Salad', 'Breads','Curry','Rice', 'Veggies', 'Regular Mini Meal', 'Regular Full Meal', 'Special Mini Meal', 'Special Full Meal',
 'Protein mini meal', 'Protein full meal']
items = pd.read_csv('ml-100k/u.item', sep='|', names=i_cols,
 encoding='latin-1')
 
###########################################################################################################

print(users.shape)
print(users.head(25))

###########################################################################################################

print(ratings.shape)
print(ratings.head(25))

###########################################################################################################

print(items.shape)
print(items.head(25))

###########################################################################################################

r_cols = ['user_id', 'dish_id', 'rating', 'unix_timestamp']
ratings_train = pd.read_csv('ml-100k/ua.base', sep='\t', names=r_cols, encoding='latin-1')
ratings_test = pd.read_csv('ml-100k/ua.test', sep='\t', names=r_cols, encoding='latin-1')
ratings_train.shape, ratings_test.shape
print(ratings_train.head(25))

###########################################################################################################

n_users = ratings.user_id.shape[0]
n_items = ratings.dish_id.unique().shape[0]
print(n_users, n_items)

###########################################################################################################

data_matrix = np.zeros((n_users, n_items))
for line in ratings.itertuples():
    data_matrix[line[1]-1, line[2]-1] = line[3]

###########################################################################################################

user_similarity = pairwise_distances(data_matrix, metric='cosine')
item_similarity = pairwise_distances(data_matrix.T, metric='cosine')
print(user_similarity.shape, item_similarity.shape)
print(user_similarity)
print(item_similarity)

###########################################################################################################

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        #We use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred

###########################################################################################################

user_prediction = predict(data_matrix, user_similarity, type='user')
item_prediction = predict(data_matrix, item_similarity, type='item')
####print(user_prediction.shape, item_prediction.shape)

print(user_prediction)
print(item_prediction)

###########################################################################################################




GGG = 1
user_item_list_m = list(item_prediction[GGG])
rec_list = heapq.nlargest(20,(user_item_list_m))
print(rec_list)


rec_index = []
for elementss in rec_list:
    rec_index.append(user_item_list_m.index(elementss))
print(rec_index)

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
	cur.execute("SELECT * FROM customers WHERE username=?",(session['username'],))
	response=cur.fetchall()
	cur.execute("SELECT * FROM most_ordered ORDER BY item ASC limit 6")
	most_ordered=cur.fetchall()
	conn.close()
	return render_template('homepage_customer.html',response=response,most_ordered=most_ordered)
    



#to show items in cart
@app.route('/liked')
def liked():
	conn=sqlite3.connect('members.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM response WHERE username=?",(session['username'],))
	response=cur.fetchall()
	cur.execute("SELECT * FROM most_ordered ORDER BY item ASC limit 6")
	most_ordered=cur.fetchall()
	conn.close()
	return render_template('liked.html',response=response,most_ordered=most_ordered)

@app.route('/Nutrition')
def Nutrition():
	conn=sqlite3.connect('members.db')
	cur=conn.cursor()
	cur.execute("SELECT * FROM response WHERE username=?",(session['username'],))
	response=cur.fetchall()
	cur.execute("SELECT * FROM most_ordered ORDER BY item ASC limit 6")
	most_ordered=cur.fetchall()
	conn.close()
	return render_template('Nutrition.html',response=response,most_ordered=most_ordered)

@app.route('/search')    
def search():
	return render_template('search.html')
			
@app.route('/quantity/<place>/<rest>/<item>/<price>/<dish_image>',methods=['GET','POST'])
def quantity(place,rest,item,price,dish_image):
	return render_template('quantity.html',item=item,price=price,place=place,rest=rest,dish_image=dish_image)
	#from quantity.html , goes to /postquantity/<item>/<price>




if __name__ == '__main__':
   app.run(debug = True)	

