Overview

This AmaSift Compare is a powerful web application designed to help shoppers make informed purchasing decisions on Amazon products. This tool allows users to compare products side-by-side across multiple dimensions including price, ratings, reviews, and features.
Features

Product Comparison: Compare up to 4 products simultaneously with a clear, side-by-side view
Category Browsing: Explore products by category to find exactly what you're looking for
Advanced Filtering: Filter products by price range, rating, and category

Tech Stack

Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: MySQL

Installation
Prerequisites
Python 3.7+
MySQL Server
Node.js and npm (optional, for development tools)

Setup

Clone the repository

bashCopygit clone https://github.com/yourusername/amasift-compare.git
cd amasift-compare

Create and activate a Python virtual environment

bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies

bashCopypip install -r backend/requirements.txt

Set up environment variables
Create a .env file in the project root with the following:

CopyDB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=amasift_compare

Initialize the database

bashCopymysql -u root -p < database/schema.sql

Import data (optional)

bashCopypython backend/import_data.py path/to/your/amazon_data.csv
Running the Application

Start the backend server

bashCopypython run.py

Open your browser and navigate to http://localhost:8080

Project Structure
Copyamasift-compare/
├── backend/                 # Flask backend
│   ├── models/              # Database models
│   ├── routes/              # API routes
│   ├── services/            # Business logic
│   ├── utils/               # Utility functions
│   ├── app.py               # Main Flask application
│   └── import_data.py       # Data import script
├── frontend/                # Web frontend
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   ├── images/              # Static images
│   └── index.html           # Main HTML file
├── database/                # Database scripts
│   └── schema.sql           # Database schema
├── .env                     # Environment variables (create this yourself)
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
API Endpoints

GET /api/categories: Get all product categories
GET /api/products: Get products with optional filtering
GET /api/products/deals: Get products with highest discount percentage
POST /api/compare: Compare multiple products
GET /api/reviews/product/{product_id}: Get reviews for a specific product
GET /api/reviews/stats/{product_id}: Get review statistics for a product
GET /api/reviews/sentiment/{product_id}: Get sentiment analysis for product reviews

Future Enhancements

User accounts for saving product comparisons
Integration with more e-commerce platforms
Price history tracking and price drop alerts
Mobile application version
Machine learning for personalized product recommendations

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

Data sourced from Kaggle's "Amazon Sales Data" dataset
Inspired by the need for better product comparison tools in e-commerce


Developed with ❤️ by PC
