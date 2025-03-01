"""
Category service module.
Handles business logic related to product categories.
"""
import logging
from ..utils.database import execute_query

logger = logging.getLogger(__name__)

def get_all_categories():
    """
    Get all product categories.
    
    Returns:
        list: List of category dictionaries
    """
    query = """
    SELECT DISTINCT category FROM products 
    WHERE category IS NOT NULL AND category != ''
    ORDER BY category
    """
    
    categories = execute_query(query)
    
    # Process the results to split categories with commas
    result = []
    if categories:
        # Create a set to avoid duplicates
        category_set = set()
        
        for category_dict in categories:
            category_str = category_dict['category']
            
            # Skip if the category is None or empty
            if not category_str:
                continue
                
            # Split by commas or slashes
            category_list = [c.strip() for c in category_str.replace('/', ',').split(',')]
            
            # Add each individual category
            for category in category_list:
                if category and category not in category_set:
                    category_set.add(category)
                    result.append({'category': category})
    
    # Sort the list by category name
    result.sort(key=lambda x: x['category'])
    return result

def get_category_product_count():
    """
    Get count of products in each category.
    
    Returns:
        list: List of dictionaries with category and count
    """
    query = """
    SELECT category, COUNT(*) as product_count 
    FROM products 
    WHERE category IS NOT NULL AND category != ''
    GROUP BY category
    ORDER BY product_count DESC
    """
    
    counts = execute_query(query)
    
    # Process the results for categories with commas
    result = {}
    if counts:
        for count_dict in counts:
            category_str = count_dict['category']
            product_count = count_dict['product_count']
            
            # Skip if the category is None or empty
            if not category_str:
                continue
                
            # Split by commas or slashes
            category_list = [c.strip() for c in category_str.replace('/', ',').split(',')]
            
            # Add count to each individual category
            for category in category_list:
                if category:
                    if category in result:
                        result[category] += product_count
                    else:
                        result[category] = product_count
    
    # Convert to list of dictionaries
    result_list = [{'category': k, 'product_count': v} for k, v in result.items()]
    
    # Sort by product count descending
    result_list.sort(key=lambda x: x['product_count'], reverse=True)
    return result_list