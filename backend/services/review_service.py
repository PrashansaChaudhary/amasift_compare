"""
Review service module.
Handles business logic related to product reviews.
"""
import logging
from ..utils.database import execute_query

logger = logging.getLogger(__name__)

def get_reviews_for_product(product_id, limit=10, offset=0):
    """
    Get reviews for a specific product.
    
    Args:
        product_id (str): Product ID to get reviews for
        limit (int): Maximum number of reviews to return
        offset (int): Number of reviews to skip
    
    Returns:
        list: List of review dictionaries
    """
    query = """
    SELECT * FROM reviews
    WHERE product_id = %s
    ORDER BY helpful_votes DESC, date DESC
    LIMIT %s OFFSET %s
    """
    
    reviews = execute_query(query, (product_id, limit, offset))
    return reviews or []

def get_reviews_for_products(product_ids, limit_per_product=5):
    """
    Get reviews for multiple products.
    
    Args:
        product_ids (list): List of product IDs to get reviews for
        limit_per_product (int): Maximum number of reviews per product
    
    Returns:
        list: List of review dictionaries
    """
    if not product_ids:
        return []
    
    # Create placeholders for SQL IN clause
    placeholders = ', '.join(['%s'] * len(product_ids))
    
    query = f"""
    SELECT r.*
    FROM (
        SELECT 
            reviews.*,
            ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY helpful_votes DESC, date DESC) as row_num
        FROM reviews
        WHERE product_id IN ({placeholders})
    ) r
    WHERE r.row_num <= %s
    ORDER BY r.product_id, r.helpful_votes DESC, r.date DESC
    """
    
    params = list(product_ids)
    params.append(limit_per_product)
    
    reviews = execute_query(query, params)
    return reviews or []

def get_review_statistics(product_id):
    """
    Get review statistics for a product.
    
    Args:
        product_id (str): Product ID to get statistics for
    
    Returns:
        dict: Dictionary with review statistics
    """
    query = """
    SELECT 
        COUNT(*) as review_count,
        AVG(rating) as average_rating,
        SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_reviews,
        SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) as negative_reviews,
        AVG(sentiment_score) as average_sentiment
    FROM reviews
    WHERE product_id = %s
    """
    
    result = execute_query(query, (product_id,))
    
    if not result:
        return {
            'review_count': 0,
            'average_rating': 0,
            'positive_reviews': 0,
            'negative_reviews': 0,
            'average_sentiment': 0
        }
    
    stats = result[0]
    
    # Add rating distribution
    query_distribution = """
    SELECT 
        rating,
        COUNT(*) as count
    FROM reviews
    WHERE product_id = %s
    GROUP BY rating
    ORDER BY rating DESC
    """
    
    distribution = execute_query(query_distribution, (product_id,))
    
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    if distribution:
        for item in distribution:
            rating = int(item['rating'])
            if 1 <= rating <= 5:
                rating_distribution[rating] = item['count']
    
    stats['rating_distribution'] = rating_distribution
    return stats

def analyze_review_sentiment(product_id):
    """
    Analyze sentiment in reviews for a product.
    
    Args:
        product_id (str): Product ID to analyze reviews for
    
    Returns:
        dict: Dictionary with sentiment analysis
    """
    query = """
    SELECT 
        sentiment_score,
        content
    FROM reviews
    WHERE product_id = %s
    ORDER BY sentiment_score
    """
    
    reviews = execute_query(query, (product_id,))
    
    if not reviews:
        return {
            'average_sentiment': 0,
            'positive_count': 0,
            'neutral_count': 0,
            'negative_count': 0,
            'top_positive': [],
            'top_negative': []
        }
    
    # Categorize reviews by sentiment
    positive_reviews = []
    neutral_reviews = []
    negative_reviews = []
    
    total_sentiment = 0
    
    for review in reviews:
        sentiment = review['sentiment_score']
        total_sentiment += sentiment
        
        if sentiment >= 0.5:
            positive_reviews.append(review)
        elif sentiment <= -0.5:
            negative_reviews.append(review)
        else:
            neutral_reviews.append(review)
    
    # Sort by absolute sentiment score
    positive_reviews.sort(key=lambda x: x['sentiment_score'], reverse=True)
    negative_reviews.sort(key=lambda x: x['sentiment_score'])
    
    # Get top 3 positive and negative reviews
    top_positive = positive_reviews[:3]
    top_negative = negative_reviews[:3]
    
    average_sentiment = total_sentiment / len(reviews) if reviews else 0
    
    return {
        'average_sentiment': average_sentiment,
        'positive_count': len(positive_reviews),
        'neutral_count': len(neutral_reviews),
        'negative_count': len(negative_reviews),
        'top_positive': top_positive,
        'top_negative': top_negative
    }