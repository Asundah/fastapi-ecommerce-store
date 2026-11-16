# ⚡ TechHub E-Commerce Store

A complete, production-ready full-stack e-commerce application built with **FastAPI**, **Vanilla JavaScript**, and **Custom CSS**. It features a modern dark-mode storefront, a dynamic shopping cart, and real-time **M-Pesa STK Push** payment integration.

**🔴 Live Demo:** [https://techhub-ecommerce.onrender.com](https://techhub-ecommerce.onrender.com) *(Update with your actual Render URL once live)*

> **Note:** Hosted on Render's free tier. The first load may take 30 seconds to wake up the server. M-Pesa payments use the Sandbox environment.

## ✨ Features

- 🛍️ **Dynamic Storefront**: Products load dynamically from the database.
- 🛒 **Shopping Cart**: Add, view, and remove items. The cart count updates instantly without refreshing.
- 📱 **M-Pesa STK Push Integration**: Customers can pay directly via their phones using Safaricom's Daraja API.
- 🎨 **Custom UI/UX**: A sleek, responsive dark-mode design built from scratch without CSS frameworks.
- 🗄️ **Database Integration**: Fully connected to a PostgreSQL database (hosted on Neon) using SQLAlchemy.
- 🔔 **Real-time Feedback**: Custom modals and status messages for payment processing.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.8+
- **Frontend:** HTML5, Custom CSS3, Vanilla JavaScript
- **Database:** PostgreSQL (Production), SQLite (Local)
- **ORM:** SQLAlchemy
- **Payments:** Safaricom M-Pesa Daraja API
- **Deployment:** Render + Neon

## 📁 Project Structure

```text
fastapi-ecommerce-store/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI routes & M-Pesa callback logic
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic validation schemas
│   └── mpesa.py         # M-Pesa STK Push logic
├── static/
│   ├── style.css        # Custom responsive CSS
│   └── script.js        # Cart and UI logic
├── templates/
│   ├── index.html       # Storefront
│   └── cart.html        # Checkout page
├── .env.example
├── requirements.txt
└── README.md

🚀 Local Setup
1. Clone the repository
bash
git clone https://github.com/asundah/fastapi-ecommerce-store.git
cd fastapi-ecommerce-store
2. Create and activate a virtual environment
bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3. Install dependencies
bash
pip install -r requirements.txt
4. Set up Environment Variables
Create a .env file in the root directory (use .env.example as a template):

env
# Database (Leave empty to use local SQLite)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# M-Pesa Sandbox Credentials
CONSUMER_KEY=your_consumer_key
CONSUMER_SECRET=your_consumer_secret
SHORTCODE=174379
PASSKEY=your_passkey
CALLBACK_URL=https://your-ngrok-url.ngrok-free.dev/api/callback
5. Run the server
bash
uvicorn app.main:app --reload
6. Open in browser
Visit http://localhost:8000 to view the store.

📡 API Endpoints
Method	Endpoint	Description
GET	/	Serve the storefront
GET	/cart	Serve the cart page
GET	/api/products	Fetch all products
POST	/api/cart/add	Add an item to the cart
GET	/api/cart	Get cart contents & total
DELETE	/api/cart/{id}	Remove an item from cart
POST	/api/checkout	Trigger M-Pesa STK Push
POST	/api/callback	Handle M-Pesa payment confirmations
📱 How the M-Pesa Integration Works
User clicks "Pay with M-Pesa" and enters their phone number.

FastAPI calculates the total and sends an STK Push request to Safaricom.

The user receives a prompt on their phone to enter their M-Pesa PIN.

Safaricom processes the payment and sends a Callback to our /api/callback endpoint.

The database is updated, the cart is cleared, and the order is marked as "Paid".

👨‍💻 Author
Amos Asunda
GitHub: @asundah

Built with ❤️ using FastAPI, JavaScript, and M-Pesa.