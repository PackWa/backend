from datetime import datetime
from sqlalchemy.orm import backref
from app.extensions import db

from datetime import datetime
from sqlalchemy.orm import backref
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='SET NULL'))

    client = db.relationship('Client', backref=backref('orders', passive_deletes=True))
    products = db.relationship('OrderProduct', backref='order', cascade='all, delete-orphan')


class OrderProduct(db.Model):
    __tablename__ = 'order_products'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('products.id', ondelete='CASCADE'),  # Меняем на CASCADE
                           primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_order = db.Column(db.Float, nullable=False)