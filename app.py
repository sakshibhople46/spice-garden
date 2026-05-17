# ============================================================
# app.py — Task 4: SQLAlchemy ORM
# ============================================================
from flask import (Flask, render_template, request,
                   jsonify, redirect, url_for, flash)
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, login_user,
                         logout_user, login_required, current_user)
from flask_migrate import Migrate
from dotenv import load_dotenv
from functools import wraps
from urllib.parse import quote_plus
import os

from models import db, User, Category, MenuItem, Reservation, Order, OrderItem
from validators import (validate_reservation, validate_order,
                        validate_order_status, validate_reservation_status,
                        validate_registration)

load_dotenv()

app  = Flask(__name__)
CORS(app)

# ============================================================
# CONFIG
# ============================================================
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_key')
db_password = quote_plus(os.getenv('MYSQL_PASSWORD', ''))
# SQLAlchemy connection string — replaces all the MYSQL_* configs
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://"
    f"{os.getenv('MYSQL_USER', 'root')}:"
    f"{db_password}@"
    f"{os.getenv('MYSQL_HOST', 'localhost')}/"
    f"{os.getenv('MYSQL_DB', 'restaurant_db')}"
)
# Don't track every DB change in memory — saves resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ============================================================
# INIT EXTENSIONS
# ============================================================
db.init_app(app)
bcrypt  = Bcrypt(app)
migrate = Migrate(app, db)   # handles DB structure changes

login_manager = LoginManager(app)
login_manager.login_view            = 'login_page'
login_manager.login_message         = 'Please login to access this page.'
login_manager.login_message_category = 'error'

# ============================================================
# FLASK-LOGIN: load user from DB on every request
# ============================================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))   # SQLAlchemy — no cursor needed

# ============================================================
# ROLE DECORATORS
# ============================================================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_page'))
        if current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_page'))
        if current_user.role not in ('admin', 'staff'):
            flash('Staff access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# ============================================================
# AUTH ROUTES
# ============================================================
@app.route('/auth')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('auth.html')


@app.route('/auth/register', methods=['POST'])
def register():
    is_valid, result = validate_registration(request.form)
    if not is_valid:
        for error in result:
            flash(error, 'error')
        return redirect(url_for('login_page') + '?tab=register')

    # Check email already exists
    if User.query.filter_by(email=result['email']).first():
        flash('Email already registered. Please login.', 'error')
        return redirect(url_for('login_page'))

    # Hash password and save new user
    password_hash = bcrypt.generate_password_hash(
                        result['password']).decode('utf-8')
    new_user = User(
        name          = result['name'],
        email         = result['email'],
        password_hash = password_hash,
        role          = result['role']
    )
    db.session.add(new_user)
    db.session.commit()

    flash('Account created! Please login.', 'success')
    return redirect(url_for('login_page'))


@app.route('/auth/login', methods=['POST'])
def login():
    email    = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        if user.role in ('admin', 'staff'):
            return redirect(url_for('dashboard'))
        return redirect(url_for('menu'))

    flash('Invalid email or password.', 'error')
    return redirect(url_for('login_page'))


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login_page'))

# ============================================================
# PAGE ROUTES
# ============================================================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/dashboard')
@admin_required
def dashboard():
    return render_template('dashboard.html')

# ============================================================
# API — MENU
# ============================================================
@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        items = (MenuItem.query
                 .filter_by(is_available=True)
                 .join(Category)
                 .order_by(Category.id, MenuItem.name)
                 .all())
        return jsonify({'success': True, 'data': [i.to_dict() for i in items]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        cats = Category.query.order_by(Category.id).all()
        return jsonify({'success': True, 'data': [c.to_dict() for c in cats]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# API — RESERVATIONS
# ============================================================
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        rows = (Reservation.query
                .order_by(Reservation.date.desc(), Reservation.time.desc())
                .all())
        return jsonify({'success': True, 'data': [r.to_dict() for r in rows]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received.'}), 400

        is_valid, result = validate_reservation(data)
        if not is_valid:
            return jsonify({'success': False, 'errors': result}), 400

        reservation = Reservation(
            customer_name    = result['customer_name'],
            email            = result['email'],
            phone            = result['phone'],
            date             = result['date'],
            time             = result['time'],
            guests           = result['guests'],
            special_requests = result['special_requests']
        )
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'success': True,
                        'message': 'Reservation confirmed!',
                        'id': reservation.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reservations/<int:res_id>', methods=['PUT'])
def update_reservation(res_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received.'}), 400

        is_valid, result = validate_reservation_status(data)
        if not is_valid:
            return jsonify({'success': False, 'errors': result}), 400

        reservation = Reservation.query.get(res_id)
        if not reservation:
            return jsonify({'success': False, 'error': 'Reservation not found.'}), 404

        reservation.status = result['status']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reservation updated!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# API — ORDERS
# ============================================================
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify({'success': True, 'data': [o.to_dict() for o in orders]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received.'}), 400

        is_valid, result = validate_order(data)
        if not is_valid:
            return jsonify({'success': False, 'errors': result}), 400

        total = sum(float(i['price']) * int(i['quantity'])
                    for i in result['items'])
        if result['order_type'] == 'delivery':
            total += 40

        # Create the order header
        order = Order(
            customer_name        = result['customer_name'],
            table_number         = result['table_number'],
            order_type           = result['order_type'],
            total_amount         = round(total, 2),
            special_instructions = result['special_instructions']
        )
        db.session.add(order)
        db.session.flush()   # gets order.id without committing yet

        # Add each item
        for item in result['items']:
            order_item = OrderItem(
                order_id     = order.id,
                menu_item_id = int(item['menu_item_id']),
                quantity     = int(item['quantity']),
                price        = float(item['price'])
            )
            db.session.add(order_item)

        db.session.commit()   # save order + all items together
        return jsonify({'success': True,
                        'message': 'Order placed!',
                        'order_id': order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received.'}), 400

        is_valid, result = validate_order_status(data)
        if not is_valid:
            return jsonify({'success': False, 'errors': result}), 400

        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found.'}), 404

        order.status = result['status']
        db.session.commit()
        return jsonify({'success': True, 'message': 'Order updated!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# API — DASHBOARD STATS
# ============================================================
@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    try:
        from sqlalchemy import func
        from datetime import date

        today = date.today()

        today_orders = (Order.query
                        .filter(func.date(Order.created_at) == today)
                        .count())

        today_revenue = (db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
                         .filter(func.date(Order.created_at) == today,
                                 Order.status != 'cancelled')
                         .scalar())

        pending_res = Reservation.query.filter_by(status='pending').count()

        active_orders = (Order.query
                         .filter(Order.status.in_(['pending', 'preparing']))
                         .count())

        # Orders grouped by status
        by_status = (db.session.query(Order.status, func.count(Order.id))
                     .group_by(Order.status)
                     .all())
        by_status = [{'status': s, 'count': c} for s, c in by_status]

        # 5 most recent orders
        recent = (Order.query
                  .order_by(Order.created_at.desc())
                  .limit(5).all())

        # Top 5 best selling items
        top_items = (db.session.query(
                         MenuItem.name,
                         func.sum(OrderItem.quantity).label('total_ordered'))
                     .join(OrderItem, MenuItem.id == OrderItem.menu_item_id)
                     .group_by(MenuItem.id, MenuItem.name)
                     .order_by(func.sum(OrderItem.quantity).desc())
                     .limit(5).all())
        top_items = [{'name': n, 'total_ordered': int(t)} for n, t in top_items]

        return jsonify({'success': True, 'data': {
            'today_orders':         today_orders,
            'today_revenue':        float(today_revenue),
            'pending_reservations': pending_res,
            'active_orders':        active_orders,
            'orders_by_status':     by_status,
            'recent_orders':        [o.to_dict() for o in recent],
            'top_items':            top_items
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/test-db')
def test_db():
    try:
        count = MenuItem.query.count()
        return jsonify({'status': '✅ SQLAlchemy connected!', 'menu_items': count})
    except Exception as e:
        return jsonify({'status': '❌ Failed', 'error': str(e)}), 500

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    print("=" * 50)
    print("  🍛  Spice Garden — SQLAlchemy ORM active")
    print("  ➡  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)