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

def get_users():
    cur.execute('select * from users')
    users_data=cur.fetchall()
    return users_data


def check_user_exists(email):
    cur.execute("select * from users where username = %s",(email,))
    user = cur.fetchone()
    return user


def create_user(user_details):
    cur.execute("insert into users(full_name,username,password,user_type)values(%s,%s,%s,%s)",user_details)
    conn.commit()



def insert_categories(values):
    cur.execute("INSERT INTO categories( category_name,description) values(%s,%s)", values)
    conn.commit()

def insert_products(values):
    cur.execute("INSERT INTO products(category_id, product_name, specification, buying_price, selling_price, stock_quantity) values(%s,%s,%s,%s,%s,%s)", values)
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

def check_available_stock(product_id):
    cur.execute("select sum(stock_purchases.quantity_added) from stock_purchases where product_id = %s",(product_id,))
    total_stock = cur.fetchone()[0] or 0

    cur.execute("select sum(sales.quantity_sold) from sales where product_id = %s",(product_id,))
    total_sold = cur.fetchone()[0] or 0

    return total_stock - total_sold


# def get_active_users():
#     cur.execute("""
#         SELECT 
#             user_id,
#             full_name,
#             username,
#             status
#         FROM users
#         WHERE status = 'Active'
#         ORDER BY full_name
#     """)
#     get_active_users=cur.fetchall()
#     return get_active_users

def get_products_sold_below_buying_price():
    cur.execute("""
        SELECT 
            s.sale_id,
            p.product_id,
            p.product_name,
            p.specification,
            s.quantity_sold,
            p.buying_price,
            s.selling_price_at_sale,
            s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        WHERE s.selling_price_at_sale < p.buying_price
        ORDER BY s.sale_date DESC
    """)
    below_buying_price= cur.fetchall()
    return below_buying_price

def get_stock_movement_report():
    cur.execute("""
        SELECT 
            p.product_name,
            'Stock In' AS movement_type,
            st.quantity_added AS quantity,
            st.purchase_date AS movement_date
        FROM stock_purchases st
        JOIN products p ON st.product_id = p.product_id

        UNION ALL

        SELECT 
            p.product_name,
            'Stock Out' AS movement_type,
            s.quantity_sold AS quantity,
            s.sale_date AS movement_date
        FROM sales s
        JOIN products p ON s.product_id = p.product_id

        ORDER BY movement_date DESC
    """)
    movement_report=cur.fetchall()
    return movement_report

def get_sales_by_attendant():
    cur.execute("""
        SELECT 
            u.user_id,
            u.full_name,
            u.user_type,
            SUM(s.quantity_sold) AS total_items_sold,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales
        FROM sales s
        JOIN users u ON s.user_id = u.user_id
        GROUP BY u.user_id, u.full_name, u.user_type
        ORDER BY total_sales DESC
    """)
    sales_by_attendant=cur.fetchall()
    return sales_by_attendant

def get_category_profit_analysis():
    cur.execute("""
        SELECT 
            c.category_id,
            c.category_name,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales,
            SUM(s.quantity_sold * p.buying_price) AS total_cost,
            SUM((s.quantity_sold * s.selling_price_at_sale) - (s.quantity_sold * p.buying_price)) AS category_profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY category_profit DESC
    """)
    category_profit=cur.fetchall()
    return  category_profit

def get_category_sales_analysis():
    cur.execute("""
        SELECT 
            c.category_id,
            c.category_name,
            SUM(s.quantity_sold) AS total_quantity_sold,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY total_sales DESC
    """)
    category_sales=cur.fetchall()
    return category_sales

def get_profit_margin_per_product():
    cur.execute("""
        SELECT 
            product_id,
            product_name,
            specification,
            buying_price,
            selling_price,
            selling_price - buying_price AS profit_per_unit,
            ROUND(((selling_price - buying_price) / selling_price) * 100, 2) AS profit_margin_percent
        FROM products
        WHERE selling_price > 0
        ORDER BY profit_margin_percent DESC
    """)
    profit_margin=cur.fetchall()
    return profit_margin

def get_out_of_stock_products():
    cur.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.specification,
            COALESCE(st.total_stock_added, 0) - COALESCE(sa.total_sold, 0) AS available_stock
        FROM products p
        LEFT JOIN (
            SELECT product_id, SUM(quantity_added) AS total_stock_added
            FROM stock_purchases
            GROUP BY product_id
        ) st ON p.product_id = st.product_id
        LEFT JOIN (
            SELECT product_id, SUM(quantity_sold) AS total_sold
            FROM sales
            GROUP BY product_id
        ) sa ON p.product_id = sa.product_id
        WHERE COALESCE(st.total_stock_added, 0) - COALESCE(sa.total_sold, 0) <= 0
        ORDER BY p.product_name
    """)
    return cur.fetchall()



def get_total_stock_value():
    cur.execute("""
        SELECT 
            COALESCE(SUM(available_stock * buying_price), 0) AS total_stock_value
        FROM (
            SELECT 
                p.product_id,
                p.buying_price,
                COALESCE(st.total_stock_added, 0) - COALESCE(sa.total_sold, 0) AS available_stock
            FROM products p
            LEFT JOIN (
                SELECT product_id, SUM(quantity_added) AS total_stock_added
                FROM stock_purchases
                GROUP BY product_id
            ) st ON p.product_id = st.product_id
            LEFT JOIN (
                SELECT product_id, SUM(quantity_sold) AS total_sold
                FROM sales
                GROUP BY product_id
            ) sa ON p.product_id = sa.product_id
        ) stock_balance
    """)
    return cur.fetchone()[0]



def get_todays_sales():
    cur.execute("""
        SELECT 
            COALESCE(SUM(quantity_sold * selling_price_at_sale), 0) AS todays_sales
        FROM sales
        WHERE DATE(sale_date) = CURRENT_DATE
    """)
    return cur.fetchone()[0]



def get_daily_sales_summary():
    cur.execute("""
        SELECT 
            DATE(sale_date) AS sale_day,
            SUM(quantity_sold) AS total_items_sold,
            SUM(quantity_sold * selling_price_at_sale) AS total_sales
        FROM sales
        GROUP BY DATE(sale_date)
        ORDER BY sale_day DESC
    """)
    daily_sales_summary=cur.fetchall()
    return cur.fetchall()



def get_monthly_sales_summary():
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM sale_date) AS sale_year,
            EXTRACT(MONTH FROM sale_date) AS sale_month,
            SUM(quantity_sold) AS total_items_sold,
            SUM(quantity_sold * selling_price_at_sale) AS total_sales
        FROM sales
        GROUP BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
        ORDER BY sale_year DESC, sale_month DESC
    """)
    monthly_sales_summary=cur.fetchall()
    return monthly_sales_summary



def get_yearly_sales_summary():
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM sale_date) AS sale_year,
            SUM(quantity_sold) AS total_items_sold,
            SUM(quantity_sold * selling_price_at_sale) AS total_sales
        FROM sales
        GROUP BY EXTRACT(YEAR FROM sale_date)
        ORDER BY sale_year DESC
    """)
    yearly_sales_summary=cur.fetchall()
    return yearly_sales_summary



def get_profit_per_day():
    cur.execute("""
        SELECT 
            DATE(s.sale_date) AS sale_day,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales,
            SUM(s.quantity_sold * p.buying_price) AS total_cost,
            SUM((s.quantity_sold * s.selling_price_at_sale) - (s.quantity_sold * p.buying_price)) AS daily_profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY DATE(s.sale_date)
        ORDER BY sale_day DESC
    """)
    profit_per_day=cur.fetchall()
    return profit_per_day



def get_profit_per_month():
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM s.sale_date) AS sale_year,
            EXTRACT(MONTH FROM s.sale_date) AS sale_month,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales,
            SUM(s.quantity_sold * p.buying_price) AS total_cost,
            SUM((s.quantity_sold * s.selling_price_at_sale) - (s.quantity_sold * p.buying_price)) AS monthly_profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY EXTRACT(YEAR FROM s.sale_date), EXTRACT(MONTH FROM s.sale_date)
        ORDER BY sale_year DESC, sale_month DESC
    """)
    profit_per_month=cur.fetchall()
    return profit_per_month



def get_profit_per_year():
    cur.execute("""
        SELECT 
            EXTRACT(YEAR FROM s.sale_date) AS sale_year,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales,
            SUM(s.quantity_sold * p.buying_price) AS total_cost,
            SUM((s.quantity_sold * s.selling_price_at_sale) - (s.quantity_sold * p.buying_price)) AS yearly_profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY EXTRACT(YEAR FROM s.sale_date)
        ORDER BY sale_year DESC
    """)
    profit_per_year=cur.fetchall()
    return profit_per_year



def get_sales_by_product():
    cur.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.specification,
            SUM(s.quantity_sold) AS total_quantity_sold,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.specification
        ORDER BY total_sales DESC
    """)
    sales_by_product=cur.fetchall()
    return sales_by_product


def get_best_selling_products(limit=10):
    cur.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.specification,
            SUM(s.quantity_sold) AS total_quantity_sold
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.specification
        ORDER BY total_quantity_sold DESC
        LIMIT %s
    """, (limit,))
    best_selling=cur.fetchall()
    return best_selling



def get_slow_moving_products(limit=10):
    cur.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.specification,
            COALESCE(SUM(s.quantity_sold), 0) AS total_quantity_sold
        FROM products p
        LEFT JOIN sales s ON p.product_id = s.product_id
        GROUP BY p.product_id, p.product_name, p.specification
        ORDER BY total_quantity_sold ASC
        LIMIT %s
    """, (limit,))
    slow_moving=cur.fetchall()
    return slow_moving

def get_profit_per_product():
    cur.execute("""
        SELECT 
            p.product_id,
            p.product_name,
            p.specification,
            SUM(s.quantity_sold) AS total_quantity_sold,
            SUM(s.quantity_sold * s.selling_price_at_sale) AS total_sales,
            SUM(s.quantity_sold * p.buying_price) AS total_cost,
            SUM((s.quantity_sold * s.selling_price_at_sale) - (s.quantity_sold * p.buying_price)) AS gross_profit
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.specification
        ORDER BY gross_profit DESC
    """)
    profit_per_product=cur.fetchall()
    return profit_per_product
