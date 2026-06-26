import psycopg2

conn = psycopg2.connect(host='localhost',port=5432,user='postgres',password='1234',dbname='rembeka_beauty_shop')
cur = conn.cursor()

def get_products():
    cur.execute("select * from products")
    products_data = cur.fetchall()
    return products_data

def get_sales():
    cur.execute("select * from sales")
    sales_data = cur.fetchall()
    return sales_data

def get_stock_purchases():
    cur.execute("select * from stock_purchases")
    stock_purchase_data = cur.fetchall()
    return  stock_purchase_data

def get_expenses():
    cur.execute("select * from expenses")
    expenses_data = cur.fetchall()
    return expenses_data

def get_categories():
    cur.execute('select * from categories')
    categories_data=cur.fetchall()
    return categories_data


def insert_categories(values):
    cur.execute("INSERT INTO categories( category_name,description) values(%s,%s)", values)
    conn.commit()

def insert_products(values):
    cur.execute("INSERT INTO products(category_id, product_name, specification, buying_price, selling_price, stock_quantity, reorder_level, status ) values(%s,%s,%s,%s,%s,%s,%s,%s)", values)
    conn.commit()

def insert_stock_purchases(values):
    cur.execute("INSERT INTO stock_purchases( product_id, user_id, quantity_added, total_cost) values(%s,%s,%s,%s)", values)
    conn.commit()

def insert_sales(values):
    cur.execute("INSERT INTO sales( product_id, user_id, quantity_sold, selling_price_at_sale) values(%s,%s,%s,%s)", values)
    conn.commit()

def insert_expenses(values):
    cur.execute("INSERT INTO expenses( user_id, expense_name, amount, description) values(%s,%s,%s,%s)", values)
    conn.commit()

