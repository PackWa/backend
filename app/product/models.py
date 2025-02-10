from app.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(255))
    orders = db.relationship('OrderProduct',
                           backref='product',
                           cascade='all, delete-orphan',
                           passive_deletes=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'title', name='_user_product_uc'),
    )
