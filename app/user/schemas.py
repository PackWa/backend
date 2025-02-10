from app.extensions import ma
from .models import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

    id = ma.auto_field()
    first_name = ma.auto_field(required=True)
    last_name = ma.auto_field(required=True)
    phone = ma.auto_field(required=True)
    email = ma.Email(required=True)
    password = ma.String(required=True, load_only=True)