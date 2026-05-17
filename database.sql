-- ============================================
-- RESTAURANT APP - DATABASE SETUP
-- Run this file in MySQL to create the database
-- ============================================

CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- Drop tables if they exist (for fresh setup)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS categories;

-- Categories Table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu Items Table
CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255),
    is_available BOOLEAN DEFAULT TRUE,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Reservations Table
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    guests INT NOT NULL,
    special_requests TEXT,
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    table_number INT,
    order_type ENUM('dine-in', 'takeaway', 'delivery') DEFAULT 'dine-in',
    status ENUM('pending', 'preparing', 'ready', 'delivered', 'cancelled') DEFAULT 'pending',
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    special_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items Table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    menu_item_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- ============================================
-- SAMPLE DATA
-- ============================================

INSERT INTO categories (name, icon) VALUES
('Starters', '🥗'),
('Main Course', '🍛'),
('Pizzas', '🍕'),
('Burgers', '🍔'),
('Desserts', '🍰'),
('Beverages', '🥤');

INSERT INTO menu_items (category_id, name, description, price, is_vegetarian) VALUES
(1, 'Veg Spring Rolls', 'Crispy rolls filled with seasoned vegetables', 180.00, TRUE),
(1, 'Chicken Wings', 'Spicy buffalo wings with dipping sauce', 320.00, FALSE),
(1, 'Bruschetta', 'Toasted bread with tomatoes and basil', 200.00, TRUE),
(1, 'Soup of the Day', 'Freshly made daily seasonal soup', 150.00, TRUE),
(2, 'Paneer Butter Masala', 'Cottage cheese in rich tomato gravy', 350.00, TRUE),
(2, 'Chicken Biryani', 'Aromatic basmati rice with spiced chicken', 420.00, FALSE),
(2, 'Dal Makhani', 'Slow-cooked black lentils with cream', 280.00, TRUE),
(2, 'Grilled Fish', 'Herb-marinated fish with lemon butter', 480.00, FALSE),
(3, 'Margherita Pizza', 'Classic tomato sauce with mozzarella', 380.00, TRUE),
(3, 'Pepperoni Pizza', 'Loaded with pepperoni and cheese', 480.00, FALSE),
(3, 'BBQ Chicken Pizza', 'BBQ sauce, chicken, onions, peppers', 500.00, FALSE),
(4, 'Classic Cheeseburger', 'Beef patty with cheese and fresh veggies', 320.00, FALSE),
(4, 'Veggie Burger', 'Grilled veggie patty with special sauce', 260.00, TRUE),
(4, 'Crispy Chicken Burger', 'Fried chicken fillet with coleslaw', 340.00, FALSE),
(5, 'Chocolate Lava Cake', 'Warm cake with molten chocolate center', 220.00, TRUE),
(5, 'Gulab Jamun', 'Soft milk solids in rose sugar syrup', 150.00, TRUE),
(5, 'Ice Cream Sundae', 'Three scoops with toppings of choice', 180.00, TRUE),
(6, 'Fresh Lime Soda', 'Chilled lime soda sweet or salted', 80.00, TRUE),
(6, 'Mango Lassi', 'Thick and creamy mango yogurt drink', 120.00, TRUE),
(6, 'Cold Coffee', 'Blended coffee with ice cream', 150.00, TRUE);

-- Sample Reservations
INSERT INTO reservations (customer_name, email, phone, date, time, guests, status) VALUES
('Priya Sharma', 'priya@example.com', '9876543210', CURDATE(), '19:00:00', 4, 'confirmed'),
('Rahul Mehta', 'rahul@example.com', '9123456789', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '20:00:00', 2, 'pending'),
('Anita Desai', 'anita@example.com', '9988776655', DATE_ADD(CURDATE(), INTERVAL 2 DAY), '13:00:00', 6, 'confirmed');

-- Sample Orders
INSERT INTO orders (customer_name, table_number, order_type, status, total_amount) VALUES
('Table 3 Customer', 3, 'dine-in', 'preparing', 750.00),
('Vikram S', NULL, 'takeaway', 'ready', 420.00),
('Table 7 Customer', 7, 'dine-in', 'pending', 1100.00);

SELECT 'Database setup complete! Tables created and sample data inserted.' AS message;

USE restaurant_db;
SELECT * FROM reservations;
SELECT * FROM orders;
SELECT * FROM menu_items;