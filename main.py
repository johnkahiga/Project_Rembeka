from flask import Flask, render_template,request,redirect,url_for,flash,session
from database import get_products,get_categories,get_expenses,get_sales,get_stock_purchases

from flask_bcrypt import Bcrypt
from functools import wraps 


app = Flask(__name__)

bcrypt = Bcrypt(app)


app.secret_key = 'fhgjhngugndfgkutrgj'

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/products')
def products():
    product_data=get_products()
    return render_template("products.html",product_data=product_data)

@app.route('/stockpurchases')
def stockpurchases():
    return render_template("stockpurchases.html")

@app.route('/sales')
def sales():
    return render_template("sales.html")

@app.route('/expenses')
def expenses():
    return render_template("expenses.html")

@app.route('/categories')
def categories():
    return render_template("categories.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")





app.run()