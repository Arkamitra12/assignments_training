import json
import os
# ==========================================
# TASK 1: LOAD CUSTOMER RETURN REQUESTS
# ==========================================
def load_returns():
   file_path = "returns.json"
   # Check whether the file exists
   if not os.path.exists(file_path):
       print("Error: returns.json file not found!")
       return []
   # Load JSON data
   try:
       with open(file_path, "r", encoding="utf-8") as file:
           returns = json.load(file)
       print("\n========== CUSTOMER RETURN REQUESTS ==========")
       print(f"\nTotal requests loaded: {len(returns)}")
       # Display each customer request
       for request in returns:
           print("\n----------------------------------")
           print("Request ID:", request["request_id"])
           print("Order ID:", request["order_id"])
           print("Product:", request["product"])
           print("Category:", request["product_category"])
           print("Request Type:", request["request_type"])
           print("Amount:", request["amount_inr"])
           print("Days Since Delivery:", request["days_since_delivery"])
           print("Item Condition:", request["item_condition"])
           print("Return Reason:", request["return_reason"])
           print("Invoice Available:", request["invoice_available"])
           print("Photo Evidence:", request["photo_evidence_available"])
           print("Previous Returns:", request["previous_returns_90_days"])
       return returns
   except json.JSONDecodeError:
       print("Error: Invalid JSON format!")
       return []
   except KeyError as e:
       print(f"Error: Missing field {e}")
       return []

# ==========================================
# MAIN PROGRAM
# ==========================================
if __name__ == "__main__":
   customer_requests = load_returns()
   print("\n==================================")
   print("TASK 1 EXECUTION COMPLETED")
   print("Total Records:", len(customer_requests))
   print("==================================")
