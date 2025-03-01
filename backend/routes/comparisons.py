"""
Comparisons route module.
Handles HTTP requests related to product comparisons.
"""
import logging
from flask import request, jsonify
from . import comparisons_bp
from ..services import comparison_service
import uuid

logger = logging.getLogger(__name__)

@comparisons_bp.route('', methods=['POST'])
def compare_products():
    """
    Compare two or more products.
    
    Body Parameters (JSON):
        product_ids (list): List of product IDs to compare
        session_id (str, optional): Session identifier for saving history
    
    Returns:
        JSON: Comparison results with product information
    """
    try:
        data = request.get_json()
        
        if not data or 'product_ids' not in data:
            return jsonify({"error": "Please provide product_ids in the request body"}), 400
            
        product_ids = data.get('product_ids', [])
        
        if len(product_ids) < 2:
            return jsonify({"error": "Please provide at least two product IDs for comparison"}), 400
        
        # Get session ID for history saving (optional)
        session_id = data.get('session_id')
        
        # If no session ID provided, generate one
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get comparison results
        comparison_result = comparison_service.compare_products(product_ids)
        
        # Save to history if we have a session ID
        comparison_service.save_comparison_history(session_id, product_ids)
        
        # Add session ID to response for client to save
        comparison_result['session_id'] = session_id
        
        return jsonify(comparison_result)
    except Exception as e:
        logger.error(f"Error comparing products: {e}")
        return jsonify({"error": str(e)}), 500

@comparisons_bp.route('/history', methods=['GET'])
def get_comparison_history():
    """
    Get comparison history for a session.
    
    Query Parameters:
        session_id (str): Session identifier
        limit (int): Maximum number of history items
    
    Returns:
        JSON: List of comparison history records
    """
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({"error": "Please provide a session_id parameter"}), 400
            
        limit = int(request.args.get('limit', 10))
        
        history = comparison_service.get_comparison_history(session_id, limit)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting comparison history: {e}")
        return jsonify({"error": str(e)}), 500