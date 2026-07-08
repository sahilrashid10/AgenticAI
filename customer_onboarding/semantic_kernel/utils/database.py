customers = []

def save_customer(customer):
    customers.append(customer)
    return "Customer saved successfully."

def get_all_customers():
    return customers