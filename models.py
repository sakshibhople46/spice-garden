# ============================================================
# models.py — Database models (tables as Python classes)
# ============================================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ============================================================
# USER
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('admin', 'staff', 'customer'), default='customer')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':    self.id,
            'name':  self.name,
            'email': self.email,
            'role':  self.role
        }

# ============================================================
# CATEGORY
# ============================================================
class Category(db.Model):
    __tablename__ = 'categories'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    icon       = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One category has many menu items
    menu_items = db.relationship('MenuItem', backref='category', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'icon': self.icon}

# ============================================================
# MENU ITEM
# ============================================================
class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id             = db.Column(db.Integer, primary_key=True)
    category_id    = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name           = db.Column(db.String(150), nullable=False)
    description    = db.Column(db.Text)
    price          = db.Column(db.Numeric(10, 2), nullable=False)
    image_url      = db.Column(db.String(255))
    is_available   = db.Column(db.Boolean, default=True)
    is_vegetarian  = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'name':          self.name,
            'description':   self.description,
            'price':         float(self.price),
            'is_vegetarian': self.is_vegetarian,
            'is_available':  self.is_available,
            'category_name': self.category.name if self.category else None,
            'category_icon': self.category.icon if self.category else None,
        }

# ============================================================
# RESERVATION
# ============================================================
class Reservation(db.Model):
    __tablename__ = 'reservations'

    id               = db.Column(db.Integer, primary_key=True)
    customer_name    = db.Column(db.String(150), nullable=False)
    email            = db.Column(db.String(150), nullable=False)
    phone            = db.Column(db.String(20), nullable=False)
    date             = db.Column(db.Date, nullable=False)
    time             = db.Column(db.Time, nullable=False)
    guests           = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    status           = db.Column(
                           db.Enum('pending', 'confirmed', 'cancelled'),
                           default='pending'
                       )
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':               self.id,
            'customer_name':    self.customer_name,
            'email':            self.email,
            'phone':            self.phone,
            'date':             str(self.date),
            'time':             str(self.time),
            'guests':           self.guests,
            'special_requests': self.special_requests,
            'status':           self.status,
            'created_at':       str(self.created_at)
        }

# ============================================================
# ORDER
# ============================================================
class Order(db.Model):
    __tablename__ = 'orders'

    id                   = db.Column(db.Integer, primary_key=True)
    customer_name        = db.Column(db.String(150), nullable=False)
    table_number         = db.Column(db.Integer)
    order_type           = db.Column(
                               db.Enum('dine-in', 'takeaway', 'delivery'),
                               default='dine-in'
                           )
    status               = db.Column(
                               db.Enum('pending', 'preparing', 'ready',
                                       'delivered', 'cancelled'),
                               default='pending'
                           )
    total_amount         = db.Column(db.Numeric(10, 2), default=0.00)
    special_instructions = db.Column(db.Text)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)

    # One order has many order items
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id':                   self.id,
            'customer_name':        self.customer_name,
            'table_number':         self.table_number,
            'order_type':           self.order_type,
            'status':               self.status,
            'total_amount':         float(self.total_amount),
            'special_instructions': self.special_instructions,
            'created_at':           str(self.created_at)
        }

# ============================================================
# ORDER ITEM
# ============================================================
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id           = db.Column(db.Integer, primary_key=True)
    order_id     = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    quantity     = db.Column(db.Integer, nullable=False)
    price        = db.Column(db.Numeric(10, 2), nullable=False)

    # Link back to the menu item to get its name etc.
    menu_item = db.relationship('MenuItem')

    def to_dict(self):
        return {
            'id':           self.id,
            'menu_item_id': self.menu_item_id,
            'name':         self.menu_item.name if self.menu_item else None,
            'quantity':     self.quantity,
            'price':        float(self.price)
        }