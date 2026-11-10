import json
import os

# Get the path of products.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_FILE = os.path.join(BASE_DIR, "products.json")

# Load products from JSON
def load_products():
   try:
       with open(PRODUCT_FILE, "r", encoding="utf-8") as file:
           data = json.load(file)
       # Support both list and dictionary JSON formats
       if isinstance(data, list):
           products = data
       elif isinstance(data, dict):
           products = data.get("products", [])
       else:
           raise ValueError("Invalid products.json structure.")
       # Validate product records
       required_fields = ["id", "name", "category",
                          "price_inr", "stock", "rating"]
       for product in products:
           for field in required_fields:
               if field not in product:
                   raise ValueError(
                       f"Missing field '{field}' in product: {product}"
                   )
       return products
   except FileNotFoundError:
       raise FileNotFoundError("products.json file not found.")
   except json.JSONDecodeError:
       raise ValueError("products.json contains invalid JSON.")

# ------------------------------------------------
# TOOL 1: SEARCH PRODUCTS
# ------------------------------------------------
def search_products(query: str):
   """
   Search products by product name or category.
   Returns product ID, name, category, price, stock and rating.
   """
   if not isinstance(query, str) or not query.strip():
       return {
           "status": "error",
           "message": "Please enter a valid product name or category."
       }
   products = load_products()
   query = query.strip().lower()
   matching_products = []
   for product in products:
       product_name = str(product["name"]).lower()
       category = str(product["category"]).lower()
       if query in product_name or query in category:
           matching_products.append({
               "id": product["id"],
               "name": product["name"],
               "category": product["category"],
               "price_inr": product["price_inr"],
               "stock": product["stock"],
               "rating": product["rating"]
           })
   if not matching_products:
       return {
           "status": "not_found",
           "message": f"No products found for '{query}'."
       }
   return {
       "status": "success",
       "total_matches": len(matching_products),
       "products": matching_products
   }

# ------------------------------------------------
# TOOL 2: CALCULATE ORDER TOTAL
# ------------------------------------------------
def calculate_order_total(product_id: str, quantity: int):
   """
   Calculate total order price and verify stock availability.
   """
   # Validate product ID
   if not isinstance(product_id, str) or not product_id.strip():
       return {
           "status": "error",
           "message": "Please provide a valid product ID."
       }
   # Validate quantity
   if (
       isinstance(quantity, bool)
       or not isinstance(quantity, int)
       or quantity <= 0
   ):
       return {
           "status": "error",
           "message": "Quantity must be a positive integer."
       }
   products = load_products()
   # Find the requested product
   selected_product = None
   for product in products:
       if str(product["id"]).lower() == product_id.strip().lower():
           selected_product = product
           break
   # Check whether product exists
   if selected_product is None:
       return {
           "status": "not_found",
           "message": f"Product ID '{product_id}' does not exist."
       }
   # Check available stock
   available_stock = selected_product["stock"]
   if quantity > available_stock:
       return {
           "status": "insufficient_stock",
           "product_name": selected_product["name"],
           "requested_quantity": quantity,
           "available_stock": available_stock,
           "message": "Insufficient stock available."
       }
   # Calculate total price
   unit_price = selected_product["price_inr"]
   total_cost = unit_price * quantity
   return {
       "status": "success",
       "product_id": selected_product["id"],
       "product_name": selected_product["name"],
       "unit_price": unit_price,
       "quantity": quantity,
       "total_cost": total_cost,
       "available_stock": available_stock,
       "message": "Order total calculated successfully."
   }

# ------------------------------------------------
# TEST BOTH FUNCTIONS INDEPENDENTLY
# ------------------------------------------------
if __name__ == "__main__":
   print("\n========== TEST 1: SEARCH PRODUCTS ==========")
   print(search_products("laptop"))
   print("\n========== TEST 2: CALCULATE ORDER TOTAL ==========")
   print(calculate_order_total("P101", 2))
   print("\n========== TEST 3: INSUFFICIENT STOCK ==========")
   print(calculate_order_total("P101", 100))
   print("\n========== TEST 4: INVALID QUANTITY ==========")
   print(calculate_order_total("P101", -2))
   print("\n========== TEST 5: INVALID PRODUCT ID ==========")
   print(calculate_order_total("XYZ999", 2))
   print("\n========== TEST 6: PRODUCT NOT FOUND ==========")
   print(search_products("camera"))
   print("\n========== ALL TESTS COMPLETED ==========")