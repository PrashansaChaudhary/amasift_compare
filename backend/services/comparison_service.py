"""
Comparison service module.
Handles business logic related to product comparisons.
"""
import logging
from ..utils.database import execute_query
from .product_service import get_products_by_ids
from .review_service import get_reviews_for_products

logger = logging.getLogger(__name__)

def compare_products(product_ids):
    """
    Compare multiple products and their reviews.
    
    Args:
        product_ids (list): List of product IDs to compare
    
    Returns:
        dict: Dictionary with products and comparison data
    """
    if not product_ids or len(product_ids) < 2:
        return {'error': 'At least two product IDs are required for comparison'}
    
    # Get product information
    products = get_products_by_ids(product_ids)
    if not products:
        return {'error': 'No products found for the given IDs'}
    
    # Get reviews for these products
    reviews = get_reviews_for_products(product_ids)
    
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
    
    # Calculate additional comparison metrics
    comparison_data = calculate_comparison_metrics(products)
    
    return {
        'products': products,
        'comparison': comparison_data
    }

def calculate_comparison_metrics(products):
    """
    Calculate various metrics for comparing products.
    
    Args:
        products (list): List of products with their reviews
    
    Returns:
        dict: Dictionary of comparison metrics
    """
    comparison = {
        'price_winner': None,
        'rating_winner': None,
        'review_count_winner': None,
        'discount_winner': None,
        'value_winner': None,  # Best price-to-rating ratio
    }
    
    # Find the winners for each metric
    min_price = float('inf')
    max_rating = 0
    max_review_count = 0
    max_discount = 0
    best_value = float('inf')  # Lower is better
    
    for product in products:
        product_id = product['product_id']
        price = float(product['price'] or 0)
        original_price = float(product['original_price'] or price)
        rating = float(product['rating'] or 0)
        
        # Calculate review count
        review_count = len(product.get('reviews', []))
        
        # Calculate discount percentage
        discount_percentage = 0
        if original_price > price and original_price > 0:
            discount_percentage = ((original_price - price) / original_price) * 100
        
        # Calculate value (price per rating point)
        value_ratio = float('inf')
        if rating > 0:
            value_ratio = price / rating
        
        # Update winners
        if price < min_price:
            min_price = price
            comparison['price_winner'] = product_id
            
        if rating > max_rating:
            max_rating = rating
            comparison['rating_winner'] = product_id
            
        if review_count > max_review_count:
            max_review_count = review_count
            comparison['review_count_winner'] = product_id
            
        if discount_percentage > max_discount:
            max_discount = discount_percentage
            comparison['discount_winner'] = product_id
            
        if value_ratio < best_value:
            best_value = value_ratio
            comparison['value_winner'] = product_id
    
    return comparison

def save_comparison_history(session_id, product_ids):
    """
    Save a product comparison to history.
    
    Args:
        session_id (str): User session ID
        product_ids (list): List of product IDs that were compared
    
    Returns:
        bool: True if saved successfully, False otherwise
    """
    query = """
    INSERT INTO comparison_history 
    (session_id, product_ids)
    VALUES (%s, %s)
    """
    
    # Convert list to comma-separated string
    product_ids_str = ','.join(product_ids)
    
    result = execute_query(query, (session_id, product_ids_str), fetch=False)
    return result is not None

def get_comparison_history(session_id, limit=10):
    """
    Get comparison history for a session.
    
    Args:
        session_id (str): User session ID
        limit (int): Maximum number of history items to return
    
    Returns:
        list: List of comparison history records
    """
    query = """
    SELECT * FROM comparison_history
    WHERE session_id = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    
    history = execute_query(query, (session_id, limit))
    
    # Process the results
    if history:
        for item in history:
            if 'product_ids' in item and item['product_ids']:
                item['product_ids'] = item['product_ids'].split(',')
    
    return history or []