# 🌿 Spice Garden — Fine Indian Dining Web App

A full-stack restaurant management web application built with **Flask** and **MySQL**, offering a seamless dining experience with online ordering, table reservations, and a real-time admin dashboard.

---

## 🚀 Live Preview

> Run locally at `http://localhost:5000`

---

## 📸 Screenshots

| Landing Page <img width="1920" height="978" alt="Landing page" src="https://github.com/user-attachments/assets/6187f8d6-a8b4-434a-aa14-68a2c0e1542d" />
| Reservations |<img width="1920" height="969" alt="reservation" src="https://github.com/user-attachments/assets/30b51882-092e-45bf-a66c-f43c4c564ce7" />


---

## ✨ Features

### 🏠 Landing Page
- Elegant landing page with navigation to all core features
- Highlights: Menu, Reservations, Order Now, and Dashboard
- Chef's Specials section and reserve a table

### 🍽️ Menu
- Browse the full restaurant menu by category (Starters →Food →Desserts)
- Filter by **Veg only** option
- Clean, card-based layout with dish details

### 📅 Table Reservations
- Book a table by filling name, phone, email, date, time slot, and number of guests
- View opening hours and recent bookings
- Instant confirmation flow

### 🛒 Order Now
- Choose from **3 order types**:
  - 🪑 **Dine-In** — Enter table number and name
  - 🛍️ **Takeaway** — Enter name for pickup
  - 🚚 **Delivery** — Enter name and delivery address
- Dynamic form that changes based on order type selected

### 📊 Admin Dashboard *(Login Required)*
- Secure registration and login system
- View **today's revenue** at a glance
- Track **total orders** for the day
- Monitor order status in real time:
  - 🟡 Ongoing
  - 🟠 Being Prepared
  - ✅ Ready
- Full order management interface

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | MySQL, SQLAlchemy, Alembic |
| Frontend | HTML5, CSS3, JavaScript |
| Auth | Flask session-based authentication |
| Templating | Jinja2 |

---

## 📁 Project Structure

```
spice-garden/
│
├── app.py                  # Main Flask application
├── database.sql            # Database schema
├── alembic.ini             # Database migration config
│
├── migrations/             # Alembic migration files
│
├── static/
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
│
├── templates/              # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── menu.html
│   ├── orders.html
│   ├── reservations.html
│   ├── dashboard.html
│   └── auth.html
│
├── .gitignore
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.x
- MySQL
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sakshibhople46/spice-garden.git
   cd spice-garden
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a MySQL database named `spice_garden`
   - Import the schema:
     ```bash
     mysql -u root -p spice_garden < database.sql
     ```

5. **Configure environment variables**
   - Create a `.env` file in the root directory:
     ```
     DB_HOST=localhost
     DB_USER=your_mysql_username
     DB_PASSWORD=your_mysql_password
     DB_NAME=spice_garden
     SECRET_KEY=your_secret_key
     ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Visit** `http://localhost:5000` in your browser 🎉

---

## 🔐 Authentication

- New users can **Register** with name, email, and password
- Login is required to access the **Dashboard**
- Session-based authentication managed by Flask

---

## 📍 Restaurant Info (Demo)

| Detail | Info |
|---|---|
| Location | Bandra West, Mumbai |
| Hours | Mon–Fri: 12 PM – 11 PM, Sat–Sun: 11 AM – 10:30 PM |
| Phone | +91 98765 43210 |
| Email | hello@spicegarden.in |

---

## 👩‍💻 Developer

**Sakshi Bhople**
- GitHub: [@sakshibhople46](https://github.com/sakshibhople46)

---

## 📄 License

This project was built as part of an academic assessment. All rights reserved © 2024 Spice Garden.
