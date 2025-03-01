"""
Products route module.
Handles HTTP requests related to products.
"""
import logging
from flask import request, jsonify
from . import products_bp
from backend.services import product_service, review_service

logger = logging.getLogger(__name__)

@products_bp.route('', methods=['GET'])
def get_products():
    """
    Get products with optional filtering.
    
    Query Parameters:
        category (str): Filter by category
        min_price (float): Minimum price filter
        max_price (float): Maximum price filter
        min_rating (float): Minimum rating filter
        search (str): Search term for product title/brand
        limit (int): Maximum number of results to return
        offset (int): Number of results to skip
    
    Returns:
        JSON: List of product objects
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        min_rating = request.args.get('min_rating')
        search_term = request.args.get('search')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # If search term is provided, use search function
        if search_term:
            products = product_service.search_products(search_term, limit, offset)
        else:
            # Otherwise, get products with filters
            products = product_service.get_all_products(
                category, min_price, max_price, min_rating, limit, offset
            )
        
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({"error": str(e)}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get a single product by ID.
    
    Path Parameters:
        product_id (str): Product ID to retrieve
    
    Query Parameters:
        with_reviews (bool): Include reviews in response
    
    Returns:
        JSON: Product object with optional reviews
    """
    try:
        # Get product
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Check if reviews should be included
        include_reviews = request.args.get('with_reviews', 'false').lower() == 'true'
        
        if include_reviews:
            # Get reviews for this product
            reviews = review_service.get_reviews_for_product(product_id)
            product['reviews'] = reviews
            
            # Get review statistics
            review_stats = review_service.get_review_statistics(product_id)
            product['review_stats'] = review_stats
        
        return jsonify(product)
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500

@products_bp.route('/deals', methods=['GET'])
def get_deals():
    """
    Get products with the highest discount percentage.
    
    Query Parameters:
        limit (int): Maximum number of results to return
    
    Returns:
        JSON: List of product objects with discount information
    """
    try:
        limit = int(request.args.get('limit', 10))
        deals = product_service.get_top_discounted_products(limit)
        return jsonify(deals)
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        return jsonify({"error": str(e)}), 500