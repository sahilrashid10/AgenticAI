import requests


def search_vendor(vendor_name: str):

    url = f"https://dummyjson.com/products/search?q={vendor_name}"

    response = requests.get(url)

    data = response.json()

    if not data["products"]:
        return {
            "vendor_found": False
        }

    product = data["products"][0]

    return {
        "vendor_found": True,
        "brand": product["brand"],
        "category": product["category"],
        "stock": product["stock"]
    }

def get_budget():

    return {
        "remaining_budget": 500000,
        "currency": "INR"
    }
def get_company_policy():

    return {
        "laptop_limit": 10,
        "software_limit": 5000,
        "approved_vendors": [
            "Dell",
            "HP",
            "Lenovo"
        ]
    }