import re
from datetime import datetime, timezone

from marshmallow import validates_schema, validate, fields, ValidationError
from app.extensions import ma
from .models import Order, OrderProduct
from app.product.schemas import ProductSchema

class OrderProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OrderProduct

    product_id = ma.auto_field(required=True)
    quantity = ma.auto_field(validate=validate.Range(min=1))
    price_at_order = ma.Float(validate=validate.Range(min=0.01))


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order

    id = ma.auto_field()
    title = ma.String(required=True, validate=validate.Length(min=2, max=100))
    address = ma.String(validate=validate.Length(max=200))
    date = fields.DateTime(format="iso", required=True)
    client_id = ma.auto_field()
    user_id = ma.auto_field()
    products = fields.Nested(OrderProductSchema, many=True, required=False)