from flask import Flask, render_template,request,redirect,url_for,flash,session
from database import get_products,get_categories,get_expenses,get_sales,get_users,get_stock_purchases,insert_products,insert_sales,insert_categories,insert_expenses,insert_stock_purchases,check_available_stock,check_user_exists,create_user

from flask_bcrypt import Bcrypt
from functools import wraps 


app = Flask(__name__)

bcrypt = Bcrypt(app)


app.secret_key = 'fhgjhngugndfgkutrgj'

@app.route('/')
def home():
    return render_template("index.html")

def login_required(f):
    @wraps(f)
    def protected(*args,**kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return protected

@app.route('/products')
@login_required
def products():
    product_data=get_products()
    categories=get_categories()
    return render_template("products.html",product_data=product_data,categories=categories)

@app.route('/add_products',methods=['GET','POST'])
def add_products():
    if request.method == 'POST':
        category_id = request.form['c_id']
        product_name=request.form['p_name']
        specification=request.form['spec']
        buying_price = request.form['b_price']
        selling_price = request.form['s_price']
        quantity_added=request.form['q_added']

        new_product = (category_id,product_name,specification,buying_price,selling_price,quantity_added)
        insert_products(new_product)
        flash("Product added successfully",'success') 

    return redirect(url_for('products'))


@app.route('/stockpurchases')
@login_required
def stockpurchases():
    products=get_products()
    stock=get_stock_purchases()
    users=get_users()
    return render_template("stockpurchases.html",products=products,stock=stock,users=users)

@app.route('/add_stock',methods=['GET','POST'])
def add_stock():
    if request.method == 'POST':
        pid = request.form['pid']
        uid=request.form['uid']
        quantity_added= request.form['quantity']
        total_cost=request.form['t_cost']

        new_stock = (pid,uid,quantity_added,total_cost)
        insert_stock_purchases(new_stock)
        flash("Stock added successfully",'success') 
    
    return redirect(url_for('stockpurchases'))



    

@app.route('/sales')
@login_required
def sales():
    sales_data = get_sales()
    products = get_products()
    users=get_users()
    return render_template('sales.html',sales_data=sales_data,products=products,users=users)

@app.route('/make_sale',methods=['GET','POST'])
def make_sale():
    if request.method == 'POST':
        pid = request.form['pid']
        uid=request.form['uid']
        quantity_sold= request.form['quantity']
        s_price=request.form['price']

        new_sale = (pid,uid,quantity_sold,s_price)
        available_stock = check_available_stock(pid)

        if available_stock < float(quantity_sold):
            flash("Insufficient stock,add more",'danger')
            return redirect(url_for('sales'))

        insert_sales(new_sale)
        flash("Sale added successfully",'success')
    return redirect(url_for('sales'))


@app.route('/expenses')
@login_required
def expenses():
    expenses=get_expenses()
    users=get_users()
    return render_template("expenses.html",users=users,expenses=expenses)


@app.route('/add_expense',methods=['GET','POST'])
def add_expense():
    if request.method == 'POST':
        user_id=request.form['uid']
        expense_n=request.form['expense']
        amount=request.form['amount']
        description=request.form['desc']

        new_category=(user_id,expense_n,amount,description)
        insert_expenses(new_category)
        flash("Expense  added successfully",'success')

    return redirect(url_for('expenses'))


@app.route('/categories')
@login_required
def categories():
    categories=get_categories()
    return render_template("categories.html",categories=categories)

@app.route('/add_category',methods=['GET','POST'])
def add_category():
    if request.method == 'POST':
        category_name=request.form['cid']
        description=request.form['desc']

        new_category=(category_name,description)
        insert_categories(new_category)
        flash("Category added successfully",'success')

    return redirect(url_for('categories'))




@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        user_type=request.form['type']

        existing_user = check_user_exists(email)
        if not existing_user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = (full_name,email,hashed_password,user_type)
            create_user(new_user)
            flash("User created successfully",'success')
            return redirect(url_for('login'))
        else:
            flash("User already exists,please login instead",'danger')
        
    return render_template('register.html')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        registered_user = check_user_exists(email)
        if not registered_user:
            flash("User doesn't exist,please register",'danger')
        else:
            if bcrypt.check_password_hash(registered_user[-3],password):
                session['email'] = email
                flash("Login successful",'success')
                return redirect(url_for('home'))
            else:
                flash("Incorrect password,try again",'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route('/logout')
def logout():
    session.pop('email',None)
    flash("Logged out successfully",'success')
    return redirect(url_for('login'))






app.run(debug=True)