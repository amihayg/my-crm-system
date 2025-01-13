from flask import Flask, render_template, request, redirect, url_for, flash
from customers_manager import read_customers, add_customer, get_next_customer_id, update_customer, delete_customer
from sales_manager import (read_products, read_orders, read_order_items, 
                         get_order_details, create_order, update_product, delete_product, get_next_product_id, add_product, update_order_status, delete_order, update_stock, get_low_stock_products, check_stock_availability)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # needed for flash messages

@app.route('/')
def index():
    # Get all data
    customers = read_customers()
    orders = read_orders()
    products = read_products()
    order_items = read_order_items()
    
    # Calculate statistics
    stats = {
        'total_customers': len(customers),
        'total_orders': len(orders),
        'total_products': len(products),
        'low_stock_products': len(get_low_stock_products()),
        
        # Order statistics
        'pending_orders': len([o for o in orders if o['status'] == 'pending']),
        'completed_orders': len([o for o in orders if o['status'] == 'completed']),
        
        # Sales statistics
        'total_sales': sum(float(o['total_amount']) for o in orders),
        'avg_order_value': sum(float(o['total_amount']) for o in orders) / len(orders) if orders else 0,
        
        # Recent activities
        'recent_orders': sorted(orders, key=lambda x: x['order_date'], reverse=True)[:5],
        'recent_customers': sorted(customers, key=lambda x: int(x['id']), reverse=True)[:5],
        
        # Product statistics
        'out_of_stock': len([p for p in products if int(p['stock']) == 0]),
        'total_inventory_value': sum(float(p['price']) * float(p['stock']) for p in products)
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/customers')  # New route for customers list
def customers():
    customers_list = read_customers()
    return render_template('customers.html', customers=customers_list)

@app.route('/add_customer', methods=['POST'])
def add_customer_route():
    new_customer = {
        'id': str(get_next_customer_id()),
        'customer_name': request.form['customer_name'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address']
    }
    add_customer(new_customer)
    flash('Customer added successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/orders')
def orders():
    orders = read_orders()
    return render_template('orders.html', orders=orders)

@app.route('/order/<order_id>')
def order_details(order_id):
    details = get_order_details(order_id)
    if not details:
        flash('Order not found', 'error')
        return redirect(url_for('orders'))
    return render_template('order_details.html', order=details['order'], items=details['items'])

@app.route('/products')
def products():
    products = read_products()
    return render_template('products.html', products=products)

@app.route('/new_order', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        product_ids = request.form.getlist('product_ids[]')
        quantities = request.form.getlist('quantities[]')
        
        # Create items list from form data
        items = []
        products = {p['id']: p for p in read_products()}
        
        # Validate stock availability first
        for i in range(len(product_ids)):
            if product_ids[i] and quantities[i]:  # Skip empty entries
                product = products.get(product_ids[i])
                if product:
                    if not check_stock_availability(product_ids[i], quantities[i]):
                        flash(f'Not enough stock for {product["product_name"]}. Available: {product["stock"]}', 'error')
                        customers = read_customers()
                        products = read_products()
                        return render_template('new_order.html', customers=customers, products=products)
                    
                    items.append({
                        'product_id': product_ids[i],
                        'quantity': quantities[i],
                        'price_per_unit': product['price']
                    })
        
        if items:
            order = create_order(customer_id, items)
            if order:  # Check if order creation was successful
                flash('Order created successfully!', 'success')
                return redirect(url_for('order_details', order_id=order['id']))
            else:
                flash('Failed to create order. Please check stock availability.', 'error')
        else:
            flash('Please add at least one item to the order.', 'error')
            
    customers = read_customers()
    products = read_products()
    return render_template('new_order.html', customers=customers, products=products)

@app.route('/edit_customer/<customer_id>', methods=['POST'])
def edit_customer(customer_id):
    updated_data = {
        'id': customer_id,
        'customer_name': request.form['customer_name'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address']
    }
    if update_customer(customer_id, updated_data):
        flash('Customer updated successfully!', 'success')
    else:
        flash('Failed to update customer.', 'error')
    return redirect(url_for('customers'))

@app.route('/delete_customer/<customer_id>', methods=['POST'])
def delete_customer_route(customer_id):
    if delete_customer(customer_id):
        flash('Customer deleted successfully!', 'success')
    else:
        flash('Failed to delete customer.', 'error')
    return redirect(url_for('customers'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        new_product = {
            'id': str(get_next_product_id()),
            'product_name': request.form['product_name'],
            'description': request.form['description'],
            'price': request.form['price'],
            'stock': request.form['stock']
        }
        add_product(new_product)
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        updated_data = {
            'id': product_id,
            'product_name': request.form['product_name'],
            'description': request.form['description'],
            'price': request.form['price'],
            'stock': request.form['stock']
        }
        if update_product(product_id, updated_data):
            flash('Product updated successfully!', 'success')
        else:
            flash('Failed to update product.', 'error')
        return redirect(url_for('products'))
    
    products_list = read_products()
    product = next((p for p in products_list if p['id'] == product_id), None)
    if product:
        return render_template('edit_product.html', product=product)
    flash('Product not found.', 'error')
    return redirect(url_for('products'))

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product_route(product_id):
    if delete_product(product_id):
        flash('Product deleted successfully!', 'success')
    else:
        flash('Failed to delete product.', 'error')
    return redirect(url_for('products'))

@app.route('/update_order_status/<order_id>', methods=['POST'])
def update_order_status_route(order_id):
    new_status = request.json.get('status')
    if new_status and update_order_status(order_id, new_status):
        flash('Order status updated successfully!', 'success')
        return {'success': True}
    flash('Failed to update order status.', 'error')
    return {'success': False}, 400

@app.route('/delete_order/<order_id>', methods=['POST'])
def delete_order_route(order_id):
    if delete_order(order_id):
        flash('Order deleted successfully!', 'success')
        return redirect(url_for('orders'))
    flash('Failed to delete order.', 'error')
    return redirect(url_for('orders'))

@app.route('/order_items')
def order_items():
    # Get all order items with additional details
    items = read_order_items()
    orders = {o['id']: o for o in read_orders()}
    products = {p['id']: p for p in read_products()}
    customers = {c['id']: c for c in read_customers()}
    
    # Enrich items with related data
    enriched_items = []
    for item in items:
        order = orders.get(item['order_id'])
        product = products.get(item['product_id'])
        if order and product:
            customer = customers.get(order['customer_id'])
            enriched_items.append({
                'id': item['id'],
                'order_id': item['order_id'],
                'order_date': order['order_date'],
                'customer_name': customer['customer_name'] if customer else 'Unknown',
                'product_name': product['product_name'],
                'quantity': item['quantity'],
                'price_per_unit': item['price_per_unit'],
                'total': float(item['quantity']) * float(item['price_per_unit']),
                'status': order['status']
            })
    
    return render_template('order_items.html', items=enriched_items)

@app.route('/inventory')
def inventory():
    products = read_products()
    low_stock = get_low_stock_products()
    return render_template('inventory.html', 
                         products=products, 
                         low_stock=low_stock)

@app.route('/update_stock/<product_id>', methods=['POST'])
def update_stock_route(product_id):
    quantity_change = int(request.json.get('quantity_change', 0))
    if update_stock(product_id, quantity_change):
        flash('Stock updated successfully!', 'success')
        return {'success': True}
    flash('Failed to update stock.', 'error')
    return {'success': False}, 400

@app.route('/update_stock_limit/<product_id>', methods=['POST'])
def update_stock_limit(product_id):
    data = request.json
    limit_type = data.get('type')  # 'min' or 'max'
    value = data.get('value')
    
    products = read_products()
    updated = False
    
    for product in products:
        if product['id'] == str(product_id):
            if limit_type == 'min':
                product['min_stock'] = str(value)
            else:
                product['max_stock'] = str(value)
            updated = True
            break
    
    if updated:
        write_products(products)
        return {'success': True}
    return {'success': False}, 400

if __name__ == '__main__':
    app.run(debug=True) 