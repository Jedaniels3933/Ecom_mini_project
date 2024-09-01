from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_marshmallow import Marshmallow
from datetime import date
from typing import List
from marshmallow import ValidationError, fields
from sqlalchemy import select, delete
from connection import connection
from connection import db_name, user, password, host
import datetime
from sqlalchemy import exc

#Made the updates recommended , not sure what else I can do without some more help from the tutors.

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:%21%3F12ABpp@localhost/ecom'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class= Base)
ma = Marshmallow(app)
class Customer(Base):
    __tablename__ = "customer_new"
    customer_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    email: Mapped[str] = mapped_column(db.String(50))
    phone_num: Mapped[str] = mapped_column(db.String(13))

    orders_new: Mapped[List["Orders_new"]] = db.relationship("Orders_new", back_populates='customer')
 
class Customer_accounts(Base):
    __tablename__ = "customer_accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customer_new.customer_id'), nullable=False)
    user_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    password: Mapped[str] = mapped_column(db.String(15), nullable=False)

class Orders_new(Base):
    __tablename__ = "orders_new"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customer_new.customer_id'), nullable=False)
    date: Mapped[str] = mapped_column(db.Date, nullable=False)

    customer: Mapped["Customer"] = db.relationship("Customer", back_populates='orders_new')
    products: Mapped[List["Product"]] = db.relationship("Product", secondary='order_products')

class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    orders_new: Mapped[List["Orders_new"]] = db.relationship("Orders_new", secondary='order_products')

class OrderProducts(Base):
    __tablename__ = 'order_products'
    order_id: Mapped[int] = mapped_column(db.ForeignKey('orders_new.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey('product.id'), primary_key=True)

class CustomerSchema(ma.Schema):
    id = fields.Integer(required = False)   
    customer_name = fields.String(required = True) 
    email = fields.String()
    phone_num = fields.String() 
    user_name = fields.String(required = True)
    password = fields.String(required = True)
    class Meta:
        fields = ('id', 'name', 'email', 'phone_num', 'user_name', 'password')

class OrdersSchema(ma.Schema):
    id = fields.Integer(required = False)
    date = fields.Date(required = True)
    customer_id = fields.Integer(required = True)

    class Meta:
        fields = ('id', 'date', 'customer_id', 'products')

class ProductsSchema(ma.Schema):
    id = fields.Integer(required = False)
    product_name = fields.String(required = True)
    price = fields.Float(required = True)

    class Meta:
        fields = ('id', 'product_name', 'price')
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many= True)

order_schema = OrdersSchema()
orders_schema = OrdersSchema(many= True)

product_schema = ProductsSchema()
products_schema = ProductsSchema(many= True)

@app.route('/')
def home():
    return "Welcome to the E-commerce API" 

@ app.route("/customers", methods = ['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.message), 400
    
    new_customer = Customer(user_name = customer_data['user_name'], email= customer_data['email'], phone = customer_data['phone'], username = customer_data['user_name'], password = customer_data['password'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'Message':"Customer added correctly."}), 201





@app.route("/customers", methods = ['GET'])
def get_all_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars()
    customers = result.all()

    return customers_schema.jsonify(customers)



@app.route("/customers/<int:id>", methods = ["PUT"])
def update_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalar()
    if result is None:
        return jsonify({"Error": "No customer found"}), 404
    customer = result
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    for field, value in customer_data.items():
        setattr(customer, field, value)
    db.session.commit()
    return jsonify({"Message":"Customer detail has been update. Thank you."})


@app.route("/customers/<int:id>", methods = ["DELETE"])
def delete_customer(id):
    query = delete(Customer).where(Customer.id == id)  
    result = db.session.execute(query)

    if result.rowcount == 0 :
        return jsonify({"Error": "Customer not found"}), 404

    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"}), 200

@app.route('/customer_accounts', methods=['POST'])
def create_customer_account():
    try:
        customer_account_data = CustomerSchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_customer_account = Customer_accounts(customer_id=customer_account_data['id'], user_name=customer_account_data['user_name'], password=customer_account_data['password'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message": "Customer account created successfully"}), 201   

    
@app.route("/products", methods=['POST'])
def add_product():
    try:
        product_data = ProductsSchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(product_name = product_data['product_name'], price = product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/products/<int:id>', methods=['DELETE']) # I got some help from another student 
def delete_product(id):
    query = delete(Product).where(Product.id == id)

    result = db.session.execute(query)

    if result.rowcount == 0:
        return jsonify({"Message": "Product cannot be found"}), 404
    
    db.session.commit()
    return jsonify({"Message": "This item has been deleted from the inventory. Thank you!"}), 200

@app.route("/product", methods=['GET'])
def get_products():
    query = select(Product)
    result = db.session.execute(query).scalars()
    products = result.all()
    return ProductsSchema.jsonify(products)

@app.route("/products/<int:id>", methods=['PUT'])
def update_product(id):
    query = select(Product).where(Product.id == id)
    result = db.session.execute(query).scalar()
    if result is None:
        return jsonify({"Error": "Product not found"}), 404
    product = result
    try:
        product_data = ProductsSchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    for field, value in product_data.items():
        setattr(product, field, value)
    db.session.commit()
    return jsonify({"Message": "Product updated successfully"}), 200
    
@app.route("/orders_new", methods=['POST'])
def add_order():
    try:
        order_data = OrdersSchema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_order = Orders_new(order_date = date.today(), customer_id = order_data['cust_id'])

    for order_id in order_data['items']:
        query = select(Product).where(Product.id == order_id)
        item = db.session.execute(query).scalar()
        new_order.products.append(item)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({"Message": "New order placed!"}), 201

@app.route("/orders_new", methods=['GET'])
def get_orders():
    query = select(Orders_new)
    result = db.session.execute(query).scalars()
    orders = result.all()
    return OrdersSchema.jsonify(orders)
@app.route("/order_items/<int:id>", methods = ['GET'])
def order_items(id):
    query = select(Orders_new).where(Orders_new.id == id)     
    order = db.session.execute(query).scalar()
    if order is None:
        return jsonify({"Error": "Order not found"}), 404

    return ProductsSchema.jsonify(order.products)
   




if __name__ == '__main__':
    app.run(debug = True)   

# get_orders()
# order_items()
# add_order()
# delete_product()    Testing and working 
add_customer()





