from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    clients = db.relationship('Client', backref='user', lazy=True)
    products = db.relationship('Product',
                               backref='user',
                               cascade='all, delete-orphan',
                               passive_deletes=True)
    orders = db.relationship('Order', backref='user', lazy=True)