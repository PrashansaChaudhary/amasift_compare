#!/usr/bin/env python3
import json
import csv
import mysql.connector
import os
from dotenv import load_dotenv
import sys
import re

# Load environment variables
load_dotenv()

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'amasift_compare')
}

def clean_price(price_str):
    """Extract price from price JSON."""
    if not price_str or price_str == '':
        return 0, 0
    
    try:
        # Handle JSON format
        if price_str.startswith('[{'):
            prices = json.loads(price_str)
            
            # Look for USD prices first
            usd_prices = [p for p in prices if p.get('currency') == 'USD']
            if usd_prices:
                sorted_prices = sorted(usd_prices, key=lambda p: p.get('dateAdded', ''), reverse=True)
                price = float(sorted_prices[0].get('amountMin', 0))
                original_price = float(sorted_prices[0].get('amountMax', price))
                return price, original_price
            
            # If no USD prices, use the first price
            if prices:
                price = float(prices[0].get('amountMin', 0))
                original_price = float(prices[0].get('amountMax', price))
                return price, original_price
        
        # Handle simple price format
        match = re.search(r'(\d+(\.\d+)?)', str(price_str))
        if match:
            price = float(match.group(1))
            return price, price
        
        return 0, 0
    except Exception as e:
        print("Error parsing price: {}".format(e))
        return 0, 0

def import_data(file_path):
    """Import Amazon product data."""
    # Connect to the database
    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Read the file
        print("Reading data from {}...".format(file_path))
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            # Detect delimiter (CSV or TSV)
            sample = file.read(1024)
            file.seek(0)
            
            if '\t' in sample:
                delimiter = '\t' 
                print("Using delimiter: tab")
            else:
                delimiter = ','
                print("Using delimiter: comma")
            
            csv_reader = csv.reader(file, delimiter=delimiter)
            headers = next(csv_reader)  # Read header row
            
            # Create a mapping of column indices
            column_map = {col: i for i, col in enumerate(headers)}
            
            # Import products
            products_imported = 0
            reviews_imported = 0
            
            for row in csv_reader:
                try:
                    # Skip if row is too short
                    if len(row) < min(column_map.values()):
                        print("Warning: Row has too few columns. Skipping.")
                        continue
                    
                    # Extract product information
                    product_id = row[column_map.get('asins')] if 'asins' in column_map else row[column_map.get('id')]
                    title = row[column_map.get('name')] if 'name' in column_map else ''
                    brand = row[column_map.get('brand')] if 'brand' in column_map else ''
                    category = row[column_map.get('categories')] if 'categories' in column_map else ''
                    
                    # Get prices
                    prices_str = row[column_map.get('prices')] if 'prices' in column_map else ''
                    price, original_price = clean_price(prices_str)
                    
                    # Get image and product URL
                    image_url = ''
                    product_url = ''
                    if 'reviews.sourceURLs' in column_map:
                        product_url = row[column_map.get('reviews.sourceURLs')]
                    
                    # Get rating
                    rating = 0
                    if 'reviews.rating' in column_map:
                        try:
                            rating = float(row[column_map.get('reviews.rating')])
                        except:
                            rating = 0
                    
                    # Insert product into database
                    product_query = """
                    INSERT INTO products 
                    (product_id, title, category, price, original_price, rating, image_url, product_url, brand)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    category = VALUES(category),
                    price = VALUES(price),
                    original_price = VALUES(original_price),
                    rating = VALUES(rating),
                    image_url = VALUES(image_url),
                    product_url = VALUES(product_url),
                    brand = VALUES(brand)
                    """
                    
                    cursor.execute(product_query, (
                        product_id, title, category, price, original_price, 
                        rating, image_url, product_url, brand
                    ))
                    
                    products_imported += 1
                    
                    # Handle review if present
                    if 'reviews.text' in column_map and row[column_map.get('reviews.text')]:
                        review_text = row[column_map.get('reviews.text')]
                        review_title = row[column_map.get('reviews.title')] if 'reviews.title' in column_map else ''
                        review_rating = rating  # Use the same rating we got for the product
                        
                        # Get reviewer name
                        reviewer = row[column_map.get('reviews.username')] if 'reviews.username' in column_map else ''
                        
                        # Get helpful votes
                        helpful_votes = 0
                        if 'reviews.numHelpful' in column_map:
                            try:
                                helpful_votes = int(row[column_map.get('reviews.numHelpful')])
                            except:
                                helpful_votes = 0
                        
                        # Get review date
                        review_date = None
                        if 'reviews.date' in column_map:
                            review_date_str = row[column_map.get('reviews.date')]
                            if review_date_str:
                                # Try to convert to MySQL date format
                                if 'T' in review_date_str:
                                    review_date = review_date_str.split('T')[0]
                        
                        # Insert review
                        review_query = """
                        INSERT INTO reviews 
                        (product_id, user_name, rating, title, content, helpful_votes, date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        cursor.execute(review_query, (
                            product_id, reviewer, review_rating, review_title, 
                            review_text, helpful_votes, review_date
                        ))
                        
                        reviews_imported += 1
                    
                    # Commit every 100 products
                    if products_imported % 100 == 0:
                        conn.commit()
                        print("Imported {} products, {} reviews so far...".format(products_imported, reviews_imported))
                
                except Exception as e:
                    print("Error importing product: {}".format(e))
            
            # Final commit
            conn.commit()
            print("Successfully imported {} products and {} reviews.".format(products_imported, reviews_imported))
    
    except Exception as e:
        print("Error: {}".format(e))
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    import_data(file_path)

if __name__ == "__main__":
    main()