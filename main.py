import os
from decimal import Decimal, InvalidOperation

import psycopg2
from flask import Flask, render_template,request,redirect,url_for,flash,session,abort
from database import init_app as init_database, rollback_database, get_product,update_product,get_products,get_categories,get_expenses,get_sales,get_users,get_stock_purchases,insert_products,insert_sales,insert_categories,insert_expenses,insert_stock_purchases,check_available_stock,check_user_exists,create_user,get_daily_sales_summary,get_monthly_sales_summary,get_best_selling_products,get_category_profit_analysis,get_category_sales_analysis,get_out_of_stock_products,get_products_sold_below_buying_price,get_profit_margin_per_product,get_profit_per_day,get_profit_per_month,get_profit_per_product,get_profit_per_year,get_sales_by_attendant,get_sales_by_product,get_slow_moving_products,get_stock_movement_report,get_todays_sales,get_total_stock_value,get_yearly_sales_summary
from flask_bcrypt import Bcrypt
from functools import wraps 


app = Flask(__name__)
init_database(app)

bcrypt = Bcrypt(app)


app.secret_key = os.getenv('SECRET_KEY', 'fhgjhngugndfgkutrgj')

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
@login_required
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

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = get_product(product_id)
    if product is None:
        abort(404)
    categories = get_categories()

    if request.method == 'POST':
        try:
            buying_price = Decimal(request.form['b_price'])
            selling_price = Decimal(request.form['s_price'])
            quantity = Decimal(request.form['q_added'])
            category_id = int(request.form['c_id'])
        except (InvalidOperation, ValueError, KeyError):
            flash('Enter valid product values', 'danger')
            return render_template('edit_product.html', product=product, categories=categories), 400

        if buying_price < 0 or selling_price < 0 or quantity < 0:
            flash('Prices and quantity cannot be negative', 'danger')
            return render_template('edit_product.html', product=product, categories=categories), 400

        values = (
            category_id,
            request.form['p_name'].strip(),
            request.form['spec'].strip(),
            buying_price,
            selling_price,
            quantity,
        )
        if not values[1]:
            flash('Product name is required', 'danger')
        else:
            try:
                update_product(product_id, values)
            except psycopg2.Error:
                rollback_database()
                flash('The product could not be updated. Please check the values and try again.', 'danger')
                return render_template('edit_product.html', product=product, categories=categories), 400
            flash('Product updated successfully', 'success')
            return redirect(url_for('products'))

    return render_template('edit_product.html', product=product, categories=categories)


@app.route('/stockpurchases')
@login_required
def stockpurchases():
    products=get_products()
    stock=get_stock_purchases()
    users=get_users()
    return render_template("stockpurchases.html",products=products,stock=stock,users=users)

@app.route('/add_stock',methods=['GET','POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        pid = request.form['pid']
        uid = check_user_exists(session['email'])[0]
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
@login_required
def make_sale():
    if request.method == 'POST':
        pid = request.form['pid']
        uid = check_user_exists(session['email'])[0]
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
@login_required
def add_expense():
    if request.method == 'POST':
        user_id = check_user_exists(session['email'])[0]
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
@login_required
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
   
    p_below_buying_price=get_products_sold_below_buying_price()
    stock_movement_report=get_stock_movement_report()
    sales_by_attendant=get_sales_by_attendant()
    category_profit=get_category_profit_analysis()
    category_sales=get_category_sales_analysis()
    profit_margin_per_p=get_profit_margin_per_product()
    out_of_stock_products=get_out_of_stock_products()
    total_stock_value=get_total_stock_value()
    todays_sales=get_todays_sales()
    daily_sales_summary=get_daily_sales_summary()
    monthly_sales_summary=get_monthly_sales_summary()
    yearly_sales_summary=get_yearly_sales_summary()
    profit_per_day=get_profit_per_day()
    profit_per_month=get_profit_per_month()
    profit_per_year=get_profit_per_year()
    sales_by_product=get_sales_by_product()
    best_selling_product=get_best_selling_products()
    slow_moving_products=get_slow_moving_products()
    profit_per_product=get_profit_per_product()
    return render_template("dashboard.html", p_below_buying_price= p_below_buying_price,stock_movement_report=stock_movement_report,
                          sales_by_attendant=sales_by_attendant, category_profit=category_profit,category_sales=category_sales,profit_margin_per_p=profit_margin_per_p,
                            out_of_stock_products=  out_of_stock_products, total_stock_value= total_stock_value, todays_sales= todays_sales,daily_sales_summary=daily_sales_summary
                            ,  monthly_sales_summary=  monthly_sales_summary, yearly_sales_summary= yearly_sales_summary,profit_per_day=profit_per_day,
                              profit_per_month= profit_per_month, profit_per_year= profit_per_year,   sales_by_product=  sales_by_product,best_selling_product=best_selling_product,
                              slow_moving_products=slow_moving_products,profit_per_product=profit_per_product)


@app.route('/logout')
def logout():
    session.pop('email',None)
    flash("Logged out successfully",'success')
    return redirect(url_for('login'))






if __name__ == "__main__":
    app.run(debug=True)
