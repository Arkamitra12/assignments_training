from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app=FastAPI()
class Product (BaseModel):
    name:str
    price:float
    id:int


products=[]
@app.get("/")
def home():
  return {"message":"fastapi is running"}
@app.get("/products")
def get_products():
    return products

@app.post("/products")
def add_product(product:Product):
    products.append(product)
    return{
        "message": "Product added successfully",
        "product": product
    }
@app.get("/products/{product_id}")
def get_product(product_id:int):
    for product in products:
        if product.id == product_id:
         return product


    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}")
def update_product(product_id:int,updated_product:Product):
    for index,product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product
            return updated_product
    raise HTTPException(status_code=404, detail="Product not found")





