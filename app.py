from flask import Flask, render_template, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/customers')
def customers():
    # קריאת נתוני הלקוחות מה-CSV
    df = pd.read_csv('data/customers.csv')
    customers = df.to_dict('records')
    return render_template('customers.html', customers=customers)

@app.route('/suppliers')
def suppliers():
    df = pd.read_csv('data/suppliers.csv')
    suppliers = df.to_dict('records')
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/sales')
def sales():
    # קריאת נתוני הזמנות
    orders_df = pd.read_csv('data/sales_orders.csv')
    
    # קריאת נתוני לקוחות לקבלת שמות
    customers_df = pd.read_csv('data/customers.csv')
    
    # מיזוג הטבלאות כדי לקבל את שם הלקוח
    merged_df = orders_df.merge(
        customers_df[['customer_id', 'company_name']], 
        on='customer_id'
    )
    
    # הוספת שם הלקוח לרשומות
    merged_df['customer_name'] = merged_df['company_name']
    
    orders = merged_df.to_dict('records')
    return render_template('sales.html', orders=orders)

@app.route('/purchases')
def purchases():
    # קריאת נתוני הזמנות רכש
    orders_df = pd.read_csv('data/purchase_orders.csv')
    
    # קריאת נתוני ספקים
    suppliers_df = pd.read_csv('data/suppliers.csv')
    
    # מיזוג הטבלאות
    merged_df = orders_df.merge(
        suppliers_df[['supplier_id', 'company_name']], 
        on='supplier_id'
    )
    
    # הוספת שם הספק לרשומות
    merged_df['supplier_name'] = merged_df['company_name']
    
    orders = merged_df.to_dict('records')
    suppliers = suppliers_df.to_dict('records')
    
    return render_template('purchases.html', orders=orders, suppliers=suppliers)

@app.route('/inventory')
def inventory():
    # קריאת נתוני מלאי ומוצרים
    inventory_df = pd.read_csv('data/inventory.csv')
    products_df = pd.read_csv('data/products.csv')
    
    # מיזוג הטבלאות
    merged_df = inventory_df.merge(products_df, on='product_id')
    
    # חישוב סטטוס מלאי
    def get_stock_status(row):
        if row['quantity'] < row['min_stock_level']:
            return 'Low'
        elif row['quantity'] > row['min_stock_level'] * 3:
            return 'High'
        return 'Normal'
    
    merged_df['status'] = merged_df.apply(get_stock_status, axis=1)
    
    # חישוב סטטיסטיקות
    total_items = merged_df['quantity'].sum()
    low_stock_items = len(merged_df[merged_df['status'] == 'Low'])
    total_value = (merged_df['quantity'] * merged_df['unit_price']).sum()
    
    inventory = merged_df.to_dict('records')
    
    return render_template('inventory.html',
                         inventory=inventory,
                         total_items=total_items,
                         low_stock_items=low_stock_items,
                         total_value=f"{total_value:,.2f}")

@app.route('/products')
def products():
    # קריאת נתוני מוצרים
    products_df = pd.read_csv('data/products.csv')
    suppliers_df = pd.read_csv('data/suppliers.csv')
    inventory_df = pd.read_csv('data/inventory.csv')
    
    # מיזוג עם נתוני מלאי נוכחי
    merged_df = products_df.merge(
        inventory_df[['product_id', 'quantity']], 
        on='product_id'
    )
    
    # הוספת שדה current_stock
    merged_df['current_stock'] = merged_df['quantity']
    
    products = merged_df.to_dict('records')
    suppliers = suppliers_df.to_dict('records')
    
    return render_template('products.html', 
                         products=products,
                         suppliers=suppliers)

if __name__ == '__main__':
    app.run(debug=True) 