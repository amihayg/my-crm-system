import csv
import os
from datetime import datetime

# File paths
PRODUCTS_CSV = os.path.join('data', 'products.csv')
ORDERS_CSV = os.path.join('data', 'orders.csv')
ORDER_ITEMS_CSV = os.path.join('data', 'order_items.csv')

def read_products():
    """Reads all products from the CSV."""
    products = []
    try:
        with open(PRODUCTS_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
    except FileNotFoundError:
        pass
    return products

def read_orders():
    """Reads all orders from the CSV."""
    orders = []
    try:
        with open(ORDERS_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                orders.append(row)
    except FileNotFoundError:
        pass
    return orders

def read_order_items():
    """Reads all order items from the CSV."""
    items = []
    try:
        with open(ORDER_ITEMS_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                items.append(row)
    except FileNotFoundError:
        pass
    return items

def get_order_details(order_id):
    """Gets detailed information about a specific order."""
    order = None
    order_items = []
    
    # Get order
    orders = read_orders()
    for o in orders:
        if o['id'] == str(order_id):
            order = o
            break
    
    if not order:
        return None
    
    # Get order items
    items = read_order_items()
    products = {p['id']: p for p in read_products()}
    
    for item in items:
        if item['order_id'] == str(order_id):
            product = products.get(item['product_id'])
            if product:
                order_items.append({
                    'product_name': product['product_name'],
                    'quantity': item['quantity'],
                    'price_per_unit': item['price_per_unit'],
                    'total': float(item['quantity']) * float(item['price_per_unit'])
                })
    
    return {
        'order': order,
        'items': order_items
    }

def create_order(customer_id, items):
    """Creates a new order and updates inventory."""
    # First check if all items are available
    for item in items:
        if not check_stock_availability(item['product_id'], item['quantity']):
            return None  # Not enough stock
    
    # Update stock for all items
    for item in items:
        if not update_stock(item['product_id'], -int(item['quantity'])):
            return None  # Failed to update stock
    
    # Continue with order creation as before...
    orders = read_orders()
    next_order_id = str(max([int(o['id']) for o in orders] + [0]) + 1)
    
    total_amount = sum(float(item['price_per_unit']) * float(item['quantity']) for item in items)
    
    new_order = {
        'id': next_order_id,
        'customer_id': str(customer_id),
        'order_date': datetime.now().strftime('%Y-%m-%d'),
        'total_amount': str(total_amount),
        'status': 'pending'
    }
    
    with open(ORDERS_CSV, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'customer_id', 'order_date', 'total_amount', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(new_order)
    
    next_item_id = max([int(i['id']) for i in read_order_items()] + [0]) + 1
    with open(ORDER_ITEMS_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'order_id', 'product_id', 'quantity', 'price_per_unit'])
        for item in items:
            writer.writerow({
                'id': str(next_item_id),
                'order_id': next_order_id,
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'price_per_unit': item['price_per_unit']
            })
            next_item_id += 1
    
    return new_order

# Add these functions for products management
def update_product(product_id, updated_data):
    """Updates an existing product record."""
    products = read_products()
    updated = False
    
    for i, product in enumerate(products):
        if product['id'] == str(product_id):
            # Preserve min/max stock if not in updated data
            if 'min_stock' not in updated_data:
                updated_data['min_stock'] = product.get('min_stock', '5')
            if 'max_stock' not in updated_data:
                updated_data['max_stock'] = product.get('max_stock', '100')
            products[i] = updated_data
            updated = True
            break
    
    if updated:
        write_products(products)
    return updated

def delete_product(product_id):
    """Deletes a product record."""
    products = read_products()
    original_length = len(products)
    products = [p for p in products if p['id'] != str(product_id)]
    
    if len(products) < original_length:
        write_products(products)
        return True
    return False

def write_products(products):
    """Writes the complete products list back to CSV."""
    with open(PRODUCTS_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'product_name', 'description', 'price', 'stock', 'min_stock', 'max_stock']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for product in products:
            if 'min_stock' not in product:
                product['min_stock'] = '5'  # Default minimum stock
            if 'max_stock' not in product:
                product['max_stock'] = '100'  # Default maximum stock
        
        writer.writerows(products)

def get_next_product_id():
    """Determines the next available product ID."""
    products = read_products()
    if not products:
        return 1
    return max(int(p['id']) for p in products) + 1

def add_product(product_data):
    """Adds a new product to the CSV."""
    # Add default min/max stock if not provided
    if 'min_stock' not in product_data:
        product_data['min_stock'] = '5'
    if 'max_stock' not in product_data:
        product_data['max_stock'] = '100'
    
    file_exists = os.path.isfile(PRODUCTS_CSV)
    with open(PRODUCTS_CSV, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'product_name', 'description', 'price', 'stock', 'min_stock', 'max_stock']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(product_data)

def update_order_status(order_id, new_status):
    """Updates the status of an existing order."""
    orders = read_orders()
    updated = False
    
    for i, order in enumerate(orders):
        if order['id'] == str(order_id):
            orders[i]['status'] = new_status
            updated = True
            break
    
    if updated:
        write_orders(orders)
    return updated

def delete_order(order_id):
    """Deletes an order and its items."""
    # Delete order items first
    items = read_order_items()
    items = [item for item in items if item['order_id'] != str(order_id)]
    write_order_items(items)
    
    # Then delete the order
    orders = read_orders()
    original_length = len(orders)
    orders = [o for o in orders if o['id'] != str(order_id)]
    
    if len(orders) < original_length:
        write_orders(orders)
        return True
    return False

def write_orders(orders):
    """Writes the complete orders list back to CSV."""
    with open(ORDERS_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'customer_id', 'order_date', 'total_amount', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)

def write_order_items(items):
    """Writes the complete order items list back to CSV."""
    with open(ORDER_ITEMS_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'order_id', 'product_id', 'quantity', 'price_per_unit']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items) 

# Add these inventory management functions
def update_stock(product_id, quantity_change):
    """Updates product stock. Negative quantity_change reduces stock."""
    products = read_products()
    updated = False
    
    for i, product in enumerate(products):
        if product['id'] == str(product_id):
            new_stock = int(product['stock']) + quantity_change
            min_stock = int(product.get('min_stock', '0'))
            max_stock = int(product.get('max_stock', '999999'))
            
            # Prevent stock from going negative
            if new_stock < 0:
                return False
                
            products[i]['stock'] = str(new_stock)
            updated = True
            break
    
    if updated:
        write_products(products)
    return updated

def check_stock_availability(product_id, requested_quantity):
    """Checks if there's enough stock for the requested quantity."""
    products = read_products()
    product = next((p for p in products if p['id'] == str(product_id)), None)
    if product:
        return int(product['stock']) >= int(requested_quantity)
    return False

def get_low_stock_products(threshold=None):
    """Returns list of products with stock below their minimum threshold."""
    products = read_products()
    return [p for p in products if int(p['stock']) <= int(p['min_stock'])]

def add_min_max_stock_columns():
    """Adds min_stock and max_stock columns if they don't exist."""
    products = read_products()
    if products and ('min_stock' not in products[0] or 'max_stock' not in products[0]):
        for product in products:
            if 'min_stock' not in product:
                product['min_stock'] = '5'  # Default minimum stock
            if 'max_stock' not in product:
                product['max_stock'] = '100'  # Default maximum stock
        
        with open(PRODUCTS_CSV, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'product_name', 'description', 'price', 'stock', 'min_stock', 'max_stock']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)

def initialize_sample_products():
    """Initializes sample products if the products.csv is empty."""
    products = read_products()
    if not products:
        sample_products = [
            {
                'id': '1',
                'product_name': 'Laptop',
                'description': 'Business Laptop 15"',
                'price': '999.99',
                'stock': '50',
                'min_stock': '5',
                'max_stock': '100'
            },
            {
                'id': '2',
                'product_name': 'Smartphone',
                'description': 'Latest Model 128GB',
                'price': '699.99',
                'stock': '100',
                'min_stock': '10',
                'max_stock': '200'
            },
            {
                'id': '3',
                'product_name': 'Tablet',
                'description': '10" Tablet 64GB',
                'price': '299.99',
                'stock': '75',
                'min_stock': '8',
                'max_stock': '150'
            },
            {
                'id': '4',
                'product_name': 'Headphones',
                'description': 'Wireless Noise-Canceling',
                'price': '159.99',
                'stock': '200',
                'min_stock': '15',
                'max_stock': '300'
            },
            {
                'id': '5',
                'product_name': 'Monitor',
                'description': '27" 4K Display',
                'price': '349.99',
                'stock': '30',
                'min_stock': '5',
                'max_stock': '50'
            }
        ]
        
        with open(PRODUCTS_CSV, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'product_name', 'description', 'price', 'stock', 'min_stock', 'max_stock']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_products)
        
        return True
    return False

# Call this function when the application starts
add_min_max_stock_columns()
initialize_sample_products() 