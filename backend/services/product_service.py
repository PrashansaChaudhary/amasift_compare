"""
Product service module.
Handles business logic related to products.
"""
import logging
from ..utils.database import execute_query

logger = logging.getLogger(__name__)

def get_all_products(category=None, min_price=None, max_price=None, min_rating=None, limit=100, offset=0):
    """
    Get products with optional filtering.
    
    Args:
        category (str): Filter by category
        min_price (float): Minimum price filter
        max_price (float): Maximum price filter
        min_rating (float): Minimum rating filter
        limit (int): Maximum number of results to return
        offset (int): Number of results to skip
    
    Returns:
        list: List of product dictionaries
    """
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    # Add filters if provided
    if category:
        query += " AND category LIKE %s"
        params.append(f"%{category}%")
    
    if min_price is not None:
        query += " AND price >= %s"
        params.append(float(min_price))
    
    if max_price is not None:
        query += " AND price <= %s"
        params.append(float(max_price))
        
    if min_rating is not None:
        query += " AND rating >= %s"
        params.append(float(min_rating))
    
    # Add limit and offset
    query += " ORDER BY rating DESC, price ASC LIMIT %s OFFSET %s"
    params.append(int(limit))
    params.append(int(offset))
    
    products = execute_query(query, params)
    return products or []

def get_product_by_id(product_id):
    """
    Get a single product by ID.
    
    Args:
        product_id (str): Product ID to retrieve
    
    Returns:
        dict: Product information or None if not found
    """
    query = "SELECT * FROM products WHERE product_id = %s"
    params = (product_id,)
    
    result = execute_query(query, params)
    return result[0] if result else None

def get_products_by_ids(product_ids):
    """
    Get multiple products by their IDs.
    
    Args:
        product_ids (list): List of product IDs to retrieve
    
    Returns:
        list: List of product dictionaries
    """
    if not product_ids:
        return []
        
    placeholders = ', '.join(['%s'] * len(product_ids))
    query = f"SELECT * FROM products WHERE product_id IN ({placeholders})"
    
    products = execute_query(query, product_ids)
    return products or []

def get_top_discounted_products(limit=10):
    """
    Get products with the highest discount percentage.
    
    Args:
        limit (int): Maximum number of results to return
    
    Returns:
        list: List of product dictionaries with discount information
    """
    query = """
    SELECT *, 
           ((original_price - price) / original_price * 100) as discount_percentage 
    FROM products 
    WHERE original_price > price 
    ORDER BY discount_percentage DESC 
    LIMIT %s
    """
    
    products = execute_query(query, (limit,))
    return products or []

def search_products(search_term, limit=100, offset=0):
    """
    Search products by name, brand, or category.
    
    Args:
        search_term (str): Term to search for
        limit (int): Maximum number of results to return
        offset (int): Number of results to skip
    
    Returns:
        list: List of matching product dictionaries
    """
    query = """
    SELECT * FROM products 
    WHERE title LIKE %s OR brand LIKE %s OR category LIKE %s
    ORDER BY rating DESC, price ASC
    LIMIT %s OFFSET %s
    """
    
    search_pattern = f"%{search_term}%"
    params = (search_pattern, search_pattern, search_pattern, limit, offset)
    
    products = execute_query(query, params)
    return products or []