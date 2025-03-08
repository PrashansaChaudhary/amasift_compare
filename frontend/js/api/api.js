// frontend/js/api/api.js

/**
 * API Service for AmaSift Compare
 * Handles all API requests to the backend
 */

const API_BASE_URL = '/api';

// Helper function for making API requests
async function fetchApi(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// Categories API
const categoriesApi = {
    getAll: async (withCount = false) => {
        return fetchApi(`/categories?with_count=${withCount}`);
    }
};

// Products API
const productsApi = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        
        if (params.category) queryParams.append('category', params.category);
        if (params.minPrice) queryParams.append('min_price', params.minPrice);
        if (params.maxPrice) queryParams.append('max_price', params.maxPrice);
        if (params.minRating) queryParams.append('min_rating', params.minRating);
        if (params.search) queryParams.append('search', params.search);
        if (params.limit) queryParams.append('limit', params.limit);
        if (params.offset) queryParams.append('offset', params.offset);
        
        return fetchApi(`/products?${queryParams.toString()}`);
    },
    
    getById: async (productId) => {
        return fetchApi(`/products/${productId}`);
    },
    
    getDeals: async (limit = 10) => {
        return fetchApi(`/products/deals?limit=${limit}`);
    }
};

// Comparison API
const comparisonApi = {
    compare: async (productIds = []) => {
        return fetchApi('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_ids: productIds })
        });
    },
    
    getHistory: async (sessionId, limit = 10) => {
        return fetchApi(`/compare/history?session_id=${sessionId}&limit=${limit}`);
    }
};

// Reviews API
const reviewsApi = {
    getForProduct: async (productId, limit = 10, offset = 0) => {
        return fetchApi(`/reviews/product/${productId}?limit=${limit}&offset=${offset}`);
    },
    
    getStatistics: async (productId) => {
        return fetchApi(`/reviews/stats/${productId}`);
    },
    
    getSentiment: async (productId) => {
        return fetchApi(`/reviews/sentiment/${productId}`);
    }
};

// Export all API functions
const api = {
    categories: categoriesApi,
    products: productsApi,
    comparison: comparisonApi,
    reviews: reviewsApi
};

// Make it available globally
window.api = api;