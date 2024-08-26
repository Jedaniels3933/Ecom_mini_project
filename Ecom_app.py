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

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:%21%3F12ABpp@localhost/ecom'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class= Base)
ma = Marshmallow(app)
class Customer(Base):
    __tablename__ = "customer_new"
    id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(db.String(50), nullable= False)
    email: Mapped[str] = mapped_column(db.String(50))
    phone_num: Mapped[str] = mapped_column(db.String(13))
    orders_new: Mapped[List["Orders_new"]] = db.relationship(back_populates= 'customer_new') 
 
class Customer_accounts(Base):
    __tablename__ = "customer_accounts"
    id: Mapped[int] = mapped_column(primary_key= True)
    cust_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customer_new'), nullable= False) 
    user_name: Mapped[str] = mapped_column(db.String(50), nullable= False)
    password: Mapped[str] = mapped_column(db.String(15), nullable= False)

class Orders_new(Base):
    __tablename__ = "orders_new"
    id: Mapped[int] = mapped_column(primary_key= True)
    cust_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customer_new'), nullable= False) 
    date: Mapped[date] = mapped_column(db.Date, nullable= False)
    
    product: Mapped[List['Product']] = db.relationship(secondary= cust_id)

class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key= True)
    name: Mapped[str] = mapped_column(db.String(50), nullable= False)
    price: Mapped[float] = mapped_column(db.Float, nullable= False)
    orders_new: Mapped[List['Orders_new']] = db.relationship(secondary= Orders_new)

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Integer(required = False)   
    customer_name = fields.String(required = True) 
    email = fields.String()
    phone = fields.String() 

    class Meta:
        fields = ('id', 'name', 'email', 'phone')

class OrdersSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Integer(required = False)
    order_date = fields.Date(required = True)
    customer_id = fields.Integer(required = True)

    class Meta:
        fields = ('id', 'order_date', 'cust_id', 'products')

class ProductsSchema(ma.SQLAlchemyAutoSchema):
    id = fields.Integer(required = False)
    product_name = fields.String(required = True)
    price = fields.Float(required = True)

    class Meta:
        fields = ('id', 'product_name', 'price')

@app.route('/')
def home():
    return "Welcome to the E-commerce API" 

@app.route('/customer', methods= ['POST'])
def add_customer():
    customer = Customer(name= request.json['name'], email= request.json['email'], phone_num= request.json['phone_num'])
    db.session.add(customer)
    db.session.commit()
    return jsonify("Customer added successfully")

@app.route('/customer', methods= ['GET'])
def get_customer():
    customers = Customer.query.all()
    result = Customers_Schema.dump(customers)
    return jsonify(result)

@app.route('/customer/<int:id>', methods= ['GET'])
def get_customers():
    query= select(Customer) 
    result = db.session.execute(query).scalars()
    customers= result.all()
    return Customers_Schema.jsonify(customers)

@app.route("/customers/<int:id>", methods = ["PUT"])
def update_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars()

    if result is None:
        return jsonify({"Error": "Customer not found"}), 404

    try:
        customer_data = Customer_Schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error""message"}), 400

    customer = result
    try:
        date = Customer_Schema.load
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field,value in customer_data.items():
        setattr(customer, field, value)
    db.session.commit()
    return jsonify({"message": "Customer updated successfully"}), 200


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
    data = request.get_json()
    try:
        hashed_password = generate_password_hash(data['password'])
        new_account = CustomerAccount(user_name=data['user_name'], password=hashed_password, customer_id=data['customer_id'])
        db.session.add(new_account)
        db.session.commit()
        return jsonify({'message': 'Customer account created', 'id': new_account.id}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 400
    
@app.route("/products", methods=['POST'])
def add_product():
    try:
        product_data = Product_Schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(product_name = product_data['product_name'], price = product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201
@app.route('/products/<int:id>', methods=['DELETE']) # I got some help from another student 
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted'})
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 400

@app.route("/product", methods=['GET'])
def get_products():
    query = select(Product)
    result = db.session.execute(query).scalars()
    products = result.all()
    return Products_Schema.jsonify(products)

def make_order():
    data = request.get_json()
    try:
        new_order = Orders_new(customer_id=data['cust_id'], date=datetime.utcnow())
        for i in data['products']:
            order_item = Orders_new(order_id=new_order.id, product_id=i['product_id'], quantity=i['quantity'])
            db.session.add(make_order)
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'message': 'Order placed', 'id': new_order.id}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 400
    
@app.route("/orders_new", methods=['POST'])
def add_order():
    try:
        order_data = Orders_Schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_order = Orders_new(order_date = date.today(), customer_id = order_data['cust_id'])

    for item_id in order_data['items']:
        query = select(Products).where(Products.id == item_id)
        item = db.session.execute(query).scalar()
        new_order.products.append(item)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({"Message": "New order placed!"}), 201


@app.route("/order_items/<int:id>", methods = ['GET'])
def order_items(id):
    query = select(Orders_new).where(Orders_new.id == id)     
    order = db.session.execute(query).scalar()

    return Products_Schema.jsonify(order.products)
   
app.register_error_handler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404
app.register_error_handler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400
app.register_error_handler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)   #Running successfully - Postman tests successful





