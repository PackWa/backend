from marshmallow import validate
from app.extensions import ma
from .models import Product


class ProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Product

    id = ma.auto_field()
    title = ma.auto_field(validate=validate.Length(min=2, max=100))
    description = ma.auto_field(validate=validate.Length(max=500))
    price = ma.auto_field(validate=validate.Range(min=0.01))
    photo = ma.auto_field()
    user_id = ma.auto_field()
