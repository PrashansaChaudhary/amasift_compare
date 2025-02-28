from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)  # Enable CORS for all routes

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'amasift_compare')
}

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

@app.route('/')
def index():
    """Serve the main application page."""
    return app.send_static_file('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Retrieve all product categories."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT DISTINCT category FROM products")
        categories = cursor.fetchall()
        return jsonify(categories)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products', methods=['GET'])
def get_products():
    """Retrieve products with optional filtering."""
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_rating = request.args.get('min_rating')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if min_price:
            query += " AND price >= %s"
            params.append(float(min_price))
        
        if max_price:
            query += " AND price <= %s"
            params.append(float(max_price))
            
        if min_rating:
            query += " AND rating >= %s"
            params.append(float(min_rating))
        
        query += " LIMIT 100"  # Limit results for performance
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        return jsonify(products)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/compare', methods=['POST'])
def compare_products():
    """Compare two or more products."""
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    
    if len(product_ids) < 2:
        return jsonify({"error": "Please provide at least two product IDs for comparison"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Convert list of IDs to tuple for SQL IN clause
        format_strings = ','.join(['%s'] * len(product_ids))
        query = f"SELECT * FROM products WHERE product_id IN ({format_strings})"
        
        cursor.execute(query, product_ids)
        products = cursor.fetchall()
        
        # Get reviews for these products
        review_query = f"SELECT * FROM reviews WHERE product_id IN ({format_strings})"
        cursor.execute(review_query, product_ids)
        reviews = cursor.fetchall()
        
        # Group reviews by product_id
        reviews_by_product = {}
        for review in reviews:
            product_id = review['product_id']
            if product_id not in reviews_by_product:
                reviews_by_product[product_id] = []
            reviews_by_product[product_id].append(review)
        
        # Add reviews to each product
        for product in products:
            product_id = product['product_id']
            product['reviews'] = reviews_by_product.get(product_id, [])
        
        return jsonify(products)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/top_discounts', methods=['GET'])
def get_top_discounts():
    """Get products with highest discount percentage."""
    limit = request.args.get('limit', 10)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT *, ((original_price - price) / original_price * 100) as discount_percentage 
        FROM products 
        WHERE original_price > price 
        ORDER BY discount_percentage DESC 
        LIMIT %s
        """
        
        cursor.execute(query, (int(limit),))
        products = cursor.fetchall()
        return jsonify(products)
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)