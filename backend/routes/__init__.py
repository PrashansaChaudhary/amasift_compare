"""
Routes package initialization.
This file makes the routes directory a Python package and provides functions to register routes.
"""
from flask import Blueprint

# Create blueprints
products_bp = Blueprint('products', __name__)
categories_bp = Blueprint('categories', __name__)
comparisons_bp = Blueprint('comparisons', __name__)
reviews_bp = Blueprint('reviews', __name__)

# Import route modules to ensure routes are registered
from . import products, categories, comparisons, reviews

def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(comparisons_bp, url_prefix='/api/compare')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')