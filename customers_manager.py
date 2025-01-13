import csv
import os

CUSTOMERS_CSV = os.path.join('data', 'customers.csv')

def read_customers():
    """Reads all customers from the CSV and returns a list of dicts."""
    customers = []
    try:
        with open(CUSTOMERS_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customers.append(row)
    except FileNotFoundError:
        pass
    return customers

def add_customer(customer_data):
    """Appends a new customer record to the CSV."""
    file_exists = os.path.isfile(CUSTOMERS_CSV)
    with open(CUSTOMERS_CSV, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'customer_name', 'email', 'phone', 'address']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(customer_data)

def update_customer(customer_id, updated_data):
    """Updates an existing customer record."""
    customers = read_customers()
    updated = False
    
    for i, customer in enumerate(customers):
        if customer['id'] == str(customer_id):
            customers[i] = updated_data
            updated = True
            break
    
    if updated:
        write_customers(customers)
    return updated

def delete_customer(customer_id):
    """Deletes a customer record."""
    customers = read_customers()
    original_length = len(customers)
    customers = [c for c in customers if c['id'] != str(customer_id)]
    
    if len(customers) < original_length:
        write_customers(customers)
        return True
    return False

def write_customers(customers):
    """Writes the complete customers list back to CSV."""
    with open(CUSTOMERS_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'customer_name', 'email', 'phone', 'address']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(customers)

def get_next_customer_id():
    """Determines the next available customer ID."""
    customers = read_customers()
    if not customers:
        return 1
    return max(int(c['id']) for c in customers) + 1 

def migrate_customers_add_address():
    """Add address field to existing customers."""
    customers = read_customers()
    
    # Add address field if it doesn't exist
    if customers and 'address' not in customers[0]:
        for customer in customers:
            customer['address'] = ''  # Default empty address for existing customers
        
        with open(CUSTOMERS_CSV, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'customer_name', 'email', 'phone', 'address']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(customers)

# Call this function when the application starts
migrate_customers_add_address() 