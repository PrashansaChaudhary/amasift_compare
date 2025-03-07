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
    """Get all product categories."""
    try:
        print("Attempting to fetch categories...")
        # Check if product counts should be included
        with_count = request.args.get('with_count', 'false').lower() == 'true'
        
        if with_count:
            print("Fetching categories with count...")
            categories = category_service.get_category_product_count()
        else:
            print("Fetching categories without count...")
            categories = category_service.get_all_categories()
        
        print(f"Found {len(categories) if categories else 0} categories")
        return jsonify(categories)
    except Exception as e:
        print(f"Error getting categories: {e}")
        logger.error(f"Error getting categories: {e}")
        return jsonify({"error": str(e)}), 500