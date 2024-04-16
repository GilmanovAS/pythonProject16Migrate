from datetime import datetime

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from raw_data import users, orders, offers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DFSDFGFDF'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['DEBAG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint('age<120'))
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20))
    phone = db.Column(db.String(11), unique=True)
    sex = db.Column(db.String(7))
    # offers = relationship('Order')


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = relationship('User', foreign_keys='Order.customer_id')
    executor = relationship('User', foreign_keys='Order.executor_id')


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order = relationship('Order', foreign_keys='Offer.order_id')
    executor = relationship('User', foreign_keys='Offer.executor_id')


def insert_data_orders():
    new_order = []
    for order in orders:
        new_order.append(Order(
            id=order['id'],
            name=order['name'],
            description=order['description'],
            start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
            address=order['address'],
            price=order['price'],
            customer_id=order['customer_id'],
            executor_id=order['executor_id']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_order)


def insert_data_users():
    new_user = []
    for user in users:
        new_user.append(User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            age=user['age'],
            email=user['email'],
            role=user['role'],
            phone=user['phone']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_user)


def insert_data_offers():
    new_offer = []
    for offer in offers:
        new_offer.append(Offer(
            id=offer['id'],
            order_id=offer['order_id'],
            executor_id=offer['executor_id']))
    with app.app_context():
        with db.session.begin():
            db.session.add_all(new_offer)


@app.route('/users/', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        data = []
        all_user = User.query.all()
        for user in all_user:
            data.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone})
        return jsonify(data)


@app.route('/users/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_user_pk(pk: int):
    if request.method == 'GET':
        print(pk)
        user = User.query.get(pk)
        data = {'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone
                }
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(pk)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.age = data['age']
        user.email = data['email']
        user.role = data['role']
        user.phone = data['phone']
        db.session.add(user)
        db.session.commit()
        return 'UPDATED', 200
    elif request.method == 'DELETE':
        user = User.query.get(pk)
        db.session.delete(user)
        db.session.commit()
        return 'DELETED', 200


@app.route('/orders/', methods=['GET', 'POST'])
def get_orders():
    if request.method == 'GET':
        data = []
        all_orders = Order.query.all()
        for order in all_orders:
            costomer = User.query.get(order.customer_id)
            executor = User.query.get(order.executor_id)
            data.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': costomer.last_name if costomer else 0,
                'executor_id': executor.last_name if executor else 0
            })
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        print(data)
        print(data['name'])
        new_order = Order(name=data['name'],
                          description=data['description'],
                          start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
                          end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
                          address=data['address'],
                          price=int(data['price']),
                          customer_id=int(data['customer_id']),
                          executor_id=int(data['executor_id']))
        with app.app_context():
            with db.session.begin():
                db.session.add(new_order)
        return 'OK', 200


@app.route('/orders/<int:pk>', methods=['GET', 'PUT', 'DELETE'])
def get_orders_pk(pk: int):
    if request.method == 'GET':
        print(pk)
        order = Order.query.get(pk)
        costomer = User.query.get(order.customer_id)
        executor = User.query.get(order.executor_id)
        data = {
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': costomer.last_name if costomer else 0,
            'executor_id': executor.last_name if executor else 0
        }
        return jsonify(data)
    elif request.method == 'PUT':
        data = request.get_json()
        order = Order.query.get(pk)
        order.name = data['name']
        order.description = data['description']
        order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
        order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
        order.address = data['address']
        order.price = int(data['price'])
        order.customer_id = int(data['customer_id'])
        order.executor_id = int(data['executor_id'])
        db.session.add(order)
        db.session.commit()
        return 'UPDATED', 200
    elif request.method == 'DELETE':
        order = Order.query.get(pk)
        db.session.delete(order)
        db.session.commit()
        return 'DELETED', 200


if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    # insert_data_orders()
    # insert_data_users()
    # insert_data_offers()
    with app.app_context():
        print(Order.query.first())
        print(Order.query.first().name)
    app.run()
