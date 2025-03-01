-- Database Schema for AmaSift Compare

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS amasift_compare;
USE amasift_compare;

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    rating DECIMAL(3, 1),
    rating_count INT,
    image_url VARCHAR(512),
    product_url VARCHAR(512),
    brand VARCHAR(255),
    features TEXT,
    availability VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(255),
    user_name VARCHAR(255),
    rating DECIMAL(3, 1),
    title VARCHAR(512),
    content TEXT,
    helpful_votes INT DEFAULT 0,
    date DATE,
    verified_purchase BOOLEAN DEFAULT FALSE,
    sentiment_score DECIMAL(4, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- User searches history (for potential personalization)
CREATE TABLE IF NOT EXISTS user_searches (
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    search_term VARCHAR(255),
    filters TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product comparison history
CREATE TABLE IF NOT EXISTS comparison_history (
    comparison_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    product_ids TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for improved performance
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_rating ON products(rating);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment_score);