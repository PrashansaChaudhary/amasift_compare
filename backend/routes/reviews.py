"""
Reviews route module.
Handles HTTP requests related to product reviews.
"""
import logging
from flask import request, jsonify
from . import reviews_bp
from ..services import review_service

logger = logging.getLogger(__name__)

@reviews_bp.route('/product/<product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """
    Get reviews for a specific product.
    
    Path Parameters:
        product_id (str): Product ID to get reviews for
    
    Query Parameters:
        limit (int): Maximum number of reviews to return
        offset (int): Number of reviews to skip
    
    Returns:
        JSON: List of review objects
    """
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        reviews = review_service.get_reviews_for_product(product_id, limit, offset)
        return jsonify(reviews)
    except Exception as e:
        logger.error(f"Error getting reviews for product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/stats/<product_id>', methods=['GET'])
def get_review_statistics(product_id):
    """
    Get review statistics for a product.
    
    Path Parameters:
        product_id (str): Product ID to get statistics for
    
    Returns:
        JSON: Statistics about product reviews
    """
    try:
        statistics = review_service.get_review_statistics(product_id)
        return jsonify(statistics)
    except Exception as e:
        logger.error(f"Error getting review statistics for product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/sentiment/<product_id>', methods=['GET'])
def get_review_sentiment(product_id):
    """
    Get sentiment analysis of reviews for a product.
    
    Path Parameters:
        product_id (str): Product ID to analyze reviews for
    
    Returns:
        JSON: Sentiment analysis results
    """
    try:
        sentiment = review_service.analyze_review_sentiment(product_id)
        return jsonify(sentiment)
    except Exception as e:
        logger.error(f"Error analyzing review sentiment for product {product_id}: {e}")
        return jsonify({"error": str(e)}), 500