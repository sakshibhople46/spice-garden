# ============================================================
# validators.py — Input validation for all API endpoints
# ============================================================
import re

# ---- Reusable helper functions ----

def is_valid_email(email):
    """Check email matches standard format like user@example.com"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Accept 10-digit Indian mobile numbers, optionally with +91"""
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def is_valid_date(date_str):
    """Check date is in YYYY-MM-DD format"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, date_str) is not None

def is_valid_time(time_str):
    """Check time is in HH:MM or HH:MM:SS format"""
    pattern = r'^\d{2}:\d{2}(:\d{2})?$'
    return re.match(pattern, time_str) is not None

def sanitize_string(value, max_length=255):
    """
    Strip whitespace and limit length.
    Prevents storing huge strings that could crash the DB.
    """
    if not isinstance(value, str):
        return ''
    return value.strip()[:max_length]

def is_positive_number(value):
    """Check if value can be converted to a positive number"""
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False

def is_positive_integer(value):
    """Check if value is a positive whole number"""
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


# ============================================================
# VALIDATORS — one function per API endpoint
# Each returns (is_valid: bool, errors: list)
# ============================================================

def validate_reservation(data):
    """Validate reservation form data"""
    errors = []

    # customer_name
    name = sanitize_string(data.get('customer_name', ''), 150)
    if not name:
        errors.append('Customer name is required.')
    elif len(name) < 2:
        errors.append('Name must be at least 2 characters.')

    # email
    email = sanitize_string(data.get('email', ''), 150)
    if not email:
        errors.append('Email is required.')
    elif not is_valid_email(email):
        errors.append('Invalid email format.')

    # phone
    phone = sanitize_string(data.get('phone', ''), 20)
    if not phone:
        errors.append('Phone number is required.')
    elif not is_valid_phone(phone):
        errors.append('Invalid phone. Enter a 10-digit Indian mobile number.')

    # date
    date = sanitize_string(data.get('date', ''))
    if not date:
        errors.append('Date is required.')
    elif not is_valid_date(date):
        errors.append('Invalid date format. Use YYYY-MM-DD.')

    # time
    time = sanitize_string(data.get('time', ''))
    if not time:
        errors.append('Time is required.')
    elif not is_valid_time(time):
        errors.append('Invalid time format. Use HH:MM.')

    # guests
    guests = data.get('guests')
    if guests is None:
        errors.append('Number of guests is required.')
    elif not is_positive_integer(guests):
        errors.append('Guests must be a positive number.')
    elif int(guests) > 20:
        errors.append('Maximum 20 guests per reservation.')

    # special_requests — optional, just sanitize
    special = sanitize_string(data.get('special_requests', ''), 500)

    if errors:
        return False, errors

    # Return cleaned data alongside validation result
    return True, {
        'customer_name':  name,
        'email':          email,
        'phone':          phone,
        'date':           date,
        'time':           time,
        'guests':         int(guests),
        'special_requests': special
    }


def validate_order(data):
    """Validate order placement data"""
    errors = []

    # customer_name
    name = sanitize_string(data.get('customer_name', ''), 150)
    if not name:
        errors.append('Customer name is required.')
    elif len(name) < 2:
        errors.append('Name must be at least 2 characters.')

    # order_type
    valid_types = ('dine-in', 'takeaway', 'delivery')
    order_type = data.get('order_type', 'dine-in')
    if order_type not in valid_types:
        errors.append(f'Order type must be one of: {", ".join(valid_types)}.')

    # table_number — optional, only for dine-in
    table_number = data.get('table_number')
    if table_number is not None:
        try:
            table_number = int(table_number)
            if table_number < 1 or table_number > 100:
                errors.append('Table number must be between 1 and 100.')
        except (TypeError, ValueError):
            errors.append('Table number must be a valid number.')

    # items — must exist and be a non-empty list
    items = data.get('items')
    if not items or not isinstance(items, list):
        errors.append('Order must contain at least one item.')
    else:
        if len(items) == 0:
            errors.append('Order must contain at least one item.')
        for i, item in enumerate(items):
            if not is_positive_integer(item.get('menu_item_id')):
                errors.append(f'Item {i+1}: invalid menu item ID.')
            if not is_positive_integer(item.get('quantity')):
                errors.append(f'Item {i+1}: quantity must be a positive number.')
            if int(item.get('quantity', 0)) > 50:
                errors.append(f'Item {i+1}: maximum quantity is 50.')
            if not is_positive_number(item.get('price')):
                errors.append(f'Item {i+1}: invalid price.')

    # special_instructions — optional
    special = sanitize_string(data.get('special_instructions', ''), 500)

    if errors:
        return False, errors

    return True, {
        'customer_name':        name,
        'order_type':           order_type,
        'table_number':         table_number,
        'items':                items,
        'special_instructions': special
    }


def validate_order_status(data):
    """Validate order status update"""
    allowed = ('pending', 'preparing', 'ready', 'delivered', 'cancelled')
    status = data.get('status', '')
    if status not in allowed:
        return False, [f'Status must be one of: {", ".join(allowed)}.']
    return True, {'status': status}


def validate_reservation_status(data):
    """Validate reservation status update"""
    allowed = ('pending', 'confirmed', 'cancelled')
    status = data.get('status', '')
    if status not in allowed:
        return False, [f'Status must be one of: {", ".join(allowed)}.']
    return True, {'status': status}


def validate_registration(form_data):
    """Validate user registration form"""
    errors = []

    name = sanitize_string(form_data.get('name', ''), 150)
    if not name or len(name) < 2:
        errors.append('Name must be at least 2 characters.')

    email = sanitize_string(form_data.get('email', ''), 150).lower()
    if not is_valid_email(email):
        errors.append('Invalid email format.')

    password = form_data.get('password', '')
    if len(password) < 6:
        errors.append('Password must be at least 6 characters.')
    if len(password) > 128:
        errors.append('Password too long.')

    role = form_data.get('role', 'customer')
    if role not in ('admin', 'staff', 'customer'):
        errors.append('Invalid role selected.')

    if errors:
        return False, errors

    return True, {
        'name':  name,
        'email': email,
        'password': password,
        'role':  role
    }