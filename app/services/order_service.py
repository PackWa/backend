from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.client.models import Client
from app.extensions import db
from app.order.models import Order, OrderProduct
from app.order.schemas import OrderSchema
from app.product.models import Product


class OrderService:
    @staticmethod
    def _validate_products(user_id, products_data):
        """Проверка продуктов и получение их текущих цен"""
        valid_products = []
        for item in products_data:
            product = Product.query.filter(
                Product.id == item['product_id'],
                Product.user_id == user_id
            ).first()

            if not product:
                raise ValueError(f"Product {item['product_id']} not found")

            valid_products.append({
                'product_id': product.id,
                'quantity': item.get('quantity', 1),
                'price_at_order': product.price
            })
        return valid_products

    @staticmethod
    def _validate_client(user_id, client_id):
        """Проверка существования клиента"""
        if client_id is not None:
            client = Client.query.filter(
                Client.id == client_id,
                Client.user_id == user_id
            ).first()

            if not client:
                raise ValueError("Client not found")
        return True

    @staticmethod
    def _get_product_price(product_id):
        product = Product.query.get(product_id)
        return product.price if product else None

    @staticmethod
    def create_order(user_id, order_data):
        try:
            # Валидация клиента
            OrderService._validate_client(user_id, order_data.get('client_id'))

            # Валидация и получение информации о продуктах
            products_data = OrderService._validate_products(
                user_id,
                order_data.get('products', [])
            )

            # Создание заказа
            order = Order(
                user_id=user_id,
                title=order_data['title'],
                address=order_data.get('address'),
                date=order_data['date'],
                client_id=order_data.get('client_id')
            )

            # Добавление продуктов
            for op_data in products_data:
                order.products.append(OrderProduct(**op_data))

            db.session.add(order)
            db.session.commit()
            return OrderSchema().dump(order), None

        except ValueError as e:
            return None, {'error': str(e)}
        except IntegrityError as e:
            db.session.rollback()
            return None, {'error': 'Database error'}
        except Exception as e:
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def update_order(user_id, order, update_data):
        try:
            if not order or order.user_id != user_id:
                return None, {'error': 'Order not found'}

            # Валидация клиента
            if 'client_id' in update_data:
                OrderService._validate_client(user_id, update_data.get('client_id'))

            # Обновление основных полей
            if 'title' in update_data:
                order.title = update_data['title']
            if 'address' in update_data:
                order.address = update_data.get('address')
            if 'date' in update_data:
                order.date = datetime.strptime(update_data['date'], '%Y-%m-%d').date()
            if 'client_id' in update_data:
                order.client_id = update_data.get('client_id')

            # Обновление продуктов
            if 'products' in update_data:
                # Удаляем старые продукты
                OrderProduct.query.filter_by(order_id=order.id).delete()

                # Добавляем новые с валидацией
                products_data = OrderService._validate_products(
                    user_id,
                    update_data.get('products', [])
                )

                for op_data in products_data:
                    order.products.append(OrderProduct(**op_data))

            db.session.commit()
            return OrderSchema().dump(order), None

        except ValueError as e:
            return None, {'error': str(e)}
        except IntegrityError as e:
            db.session.rollback()
            return None, {'error': 'Database error'}
        except Exception as e:
            db.session.rollback()
            return None, {'error': str(e)}

    @staticmethod
    def delete_order(order):
        if not order:
            return {'error': 'Order not found'}, 404

        try:
            db.session.delete(order)
            db.session.commit()
            return {'message': 'Order deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500