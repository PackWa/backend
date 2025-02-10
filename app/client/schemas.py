from marshmallow import validate

from app.extensions import ma
from .models import Client


class ClientSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Client

    id = ma.auto_field()
    first_name = ma.auto_field(validate=validate.Length(min=3, max=50), required=True)
    last_name = ma.auto_field(validate=validate.Length(min=3, max=50),required=False)
    phone = ma.auto_field(validate=validate.Length(min=2, max=20), required=False)
    user_id = ma.auto_field()