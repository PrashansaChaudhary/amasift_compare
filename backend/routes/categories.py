"""
Categories route module.
Handles HTTP requests related to product categories.
"""
import logging
from flask import request, jsonify
from . import categories_bp
from ..services import category_service

logger = logging.getLogger(__name__)

@categories_bp.route('', methods=['GET'])
def get_categories():
    """
    Get all product categories.
    
    Query Parameters:
        with_count (bool): Include product count for each category
    
    Returns:
        JSON: List of category objects
    """
    try:
        # Check if product counts should be included
        with_count = request.args.get('with_count', 'false').lower() == 'true'
        
        if with_count:
            categories = category_service.get_category_product_count()
        else:
            categories = category_service.get_all_categories()
            
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({"error": str(e)}), 500