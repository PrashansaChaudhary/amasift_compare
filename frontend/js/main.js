/**
 * AmaSift Compare - Main JavaScript File
 * 
 * This script handles the main functionality for the AmaSift Compare application,
 * including navigation, API calls, product comparison, and UI updates.
 */

// Constants
const API_BASE_URL = window.location.hostname === 'localhost' ? 
                    'http://localhost:5000/api' : '/api';

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    const navLinks = document.querySelectorAll('nav a, .nav-link');
    const sections = document.querySelectorAll('main > section');
    
    // Home elements
    const startComparingBtn = document.getElementById('start-comparing-btn');
    const categoryGrid = document.getElementById('category-grid');
    
    // Compare elements
    const categoryFilter = document.getElementById('category-filter');
    const priceMin = document.getElementById('price-min');
    const priceMax = document.getElementById('price-max');
    const ratingMin = document.getElementById('rating-min');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const productGrid = document.getElementById('product-grid');
    const selectedItems = document.getElementById('selected-items');
    const selectedCount = document.getElementById('selected-count');
    const compareBtn = document.getElementById('compare-btn');
    const comparisonResult = document.getElementById('comparison-result');
    
    // Templates
    const categoryTemplate = document.getElementById('category-template');
    const productCardTemplate = document.getElementById('product-card-template');
    const selectedProductTemplate = document.getElementById('selected-product-template');

    // State
    let selectedProducts = [];
    
    // Initialize the application
    init();
    
    /**
     * Initialize the application
     */
    function init() {
        // Set up event listeners
        setupNavigation();
        setupEventListeners();
        
        // Load initial data
        loadCategories();
        
        // Check if URL has parameters for direct navigation
        handleUrlParameters();
    }
    
    /**
     * Set up navigation between sections
     */
    function setupNavigation() {
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Get target section ID
                const targetId = link.getAttribute('data-target') || 
                                link.getAttribute('id').replace('nav-', '') + '-section';
                
                // Hide all sections and deactivate all links
                sections.forEach(section => section.classList.add('hidden'));
                navLinks.forEach(navLink => navLink.classList.remove('active'));
                
                // Show target section and activate link
                document.getElementById(targetId).classList.remove('hidden');
                link.classList.add('active');
                
                // Additional actions based on section
                if (targetId === 'deals-section') {
                    loadTopDeals();
                }
            });
        });
    }
    
    /**
     * Set up event listeners for buttons and interactions
     */
    function setupEventListeners() {
        // Start comparing button redirects to compare section
        startComparingBtn.addEventListener('click', () => {
            document.getElementById('nav-compare').click();
        });
        
        // Apply filters button
        applyFiltersBtn.addEventListener('click', () => {
            loadProducts();
        });
        
        // Compare button
        compareBtn.addEventListener('click', () => {
            compareProducts();
        });
    }
    
    /**
     * Load categories from API
     */
    function loadCategories() {
        categoryGrid.innerHTML = '<div class="loading">Loading categories...</div>';
        
        fetch(`${API_BASE_URL}/categories`)
            .then(response => response.json())
            .then(data => {
                categoryGrid.innerHTML = '';
                
                // Also populate category filter dropdown
                categoryFilter.innerHTML = '<option value="">All Categories</option>';
                
                data.forEach(category => {
                    // Add to category grid
                    const categoryName = category.category;
                    const categoryCard = categoryTemplate.content.cloneNode(true);
                    
                    categoryCard.querySelector('.category-name').textContent = categoryName;
                    
                    // Add click event to filter by this category
                    const cardElement = categoryCard.querySelector('.category-card');
                    cardElement.addEventListener('click', () => {
                        document.getElementById('nav-compare').click();
                        categoryFilter.value = categoryName;
                        loadProducts();
                    });
                    
                    categoryGrid.appendChild(categoryCard);
                    
                    // Add to dropdown
                    const option = document.createElement('option');
                    option.value = categoryName;
                    option.textContent = categoryName;
                    categoryFilter.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading categories:', error);
                categoryGrid.innerHTML = '<div class="error">Error loading categories. Please try again.</div>';
            });
    }
    
    /**
     * Load products based on filters
     */
    function loadProducts() {
        productGrid.innerHTML = '<div class="loading">Loading products...</div>';
        
        // Build query parameters
        const params = new URLSearchParams();
        
        if (categoryFilter.value) {
            params.append('category', categoryFilter.value);
        }
        
        if (priceMin.value) {
            params.append('min_price', priceMin.value);
        }
        
        if (priceMax.value) {
            params.append('max_price', priceMax.value);
        }
        
        if (ratingMin.value) {
            params.append('min_rating', ratingMin.value);
        }
        
        fetch(`${API_BASE_URL}/products?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                productGrid.innerHTML = '';
                
                if (data.length === 0) {
                    productGrid.innerHTML = '<div class="no-results">No products found matching your filters.</div>';
                    return;
                }
                
                data.forEach(product => {
                    renderProductCard(product);
                });
            })
            .catch(error => {
                console.error('Error loading products:', error);
                productGrid.innerHTML = '<div class="error">Error loading products. Please try again.</div>';
            });
    }
    
    /**
     * Render a product card
     */
    function renderProductCard(product) {
        const card = productCardTemplate.content.cloneNode(true);
        
        // Set product image
        const imgElement = card.querySelector('.product-image img');
        imgElement.src = product.image_url || 'images/product-placeholder.png';
        imgElement.alt = product.title;
        
        // Set product title
        card.querySelector('.product-title').textContent = product.title;
        
        // Set rating stars
        const ratingStars = card.querySelector('.rating-stars');
        const rating = parseFloat(product.rating) || 0;
        ratingStars.innerHTML = getStarRating(rating);
        
        // Set rating count
        card.querySelector('.rating-count').textContent = 
            `(${product.rating_count ? product.rating_count.toLocaleString() : 0})`;
        
        // Set prices
        const currentPrice = card.querySelector('.current-price');
        const originalPrice = card.querySelector('.original-price');
        const discountBadge = card.querySelector('.discount-badge');
        
        currentPrice.textContent = formatPrice(product.price);
        
        if (product.original_price && product.original_price > product.price) {
            originalPrice.textContent = formatPrice(product.original_price);
            
            // Calculate discount percentage
            const discountPercent = Math.round((1 - (product.price / product.original_price)) * 100);
            discountBadge.textContent = `-${discountPercent}%`;
        } else {
            originalPrice.style.display = 'none';
            discountBadge.style.display = 'none';
        }
        
        // Add to compare button
        const addButton = card.querySelector('.add-to-compare-btn');
        
        // Check if product is already selected
        const isSelected = selectedProducts.some(p => p.product_id === product.product_id);
        if (isSelected) {
            addButton.classList.add('selected');
            addButton.textContent = 'Remove from Comparison';
        }
        
        addButton.addEventListener('click', () => {
            toggleProductSelection(product, addButton);
        });
        
        productGrid.appendChild(card);
    }
    
    /**
     * Toggle product selection for comparison
     */
    function toggleProductSelection(product, button) {
        const isSelected = selectedProducts.some(p => p.product_id === product.product_id);
        
        if (isSelected) {
            // Remove from selected products
            selectedProducts = selectedProducts.filter(p => p.product_id !== product.product_id);
            button.classList.remove('selected');
            button.textContent = 'Add to Compare';
            
            // Remove from selected items display
            const selectedItem = document.querySelector(`[data-product-id="${product.product_id}"]`);
            if (selectedItem) {
                selectedItem.remove();
            }
        } else {
            // Add to selected products (max 4)
            if (selectedProducts.length >= 4) {
                alert('You can compare up to 4 products at a time. Please remove a product before adding another.');
                return;
            }
            
            selectedProducts.push(product);
            button.classList.add('selected');
            button.textContent = 'Remove from Comparison';
            
            // Add to selected items display
            renderSelectedProduct(product);
        }
        
        // Update count and compare button
        updateSelectionStatus();
    }
    
    /**
     * Render a selected product in the sidebar
     */
    function renderSelectedProduct(product) {
        const selectedItem = selectedProductTemplate.content.cloneNode(true);
        const container = selectedItem.querySelector('.selected-product');
        
        // Set product data attribute for removal
        container.setAttribute('data-product-id', product.product_id);
        
        // Set image
        const imgElement = selectedItem.querySelector('img');
        imgElement.src = product.image_url || 'images/product-placeholder.png';
        imgElement.alt = product.title;
        
        // Set title and price
        selectedItem.querySelector('.selected-product-title').textContent = product.title;
        selectedItem.querySelector('.selected-product-price').textContent = formatPrice(product.price);
        
        // Set up remove button
        const removeButton = selectedItem.querySelector('.remove-selected-btn');
        removeButton.addEventListener('click', () => {
            // Remove from selected products
            selectedProducts = selectedProducts.filter(p => p.product_id !== product.product_id);
            
            // Remove the item from the display
            container.remove();
            
            // Update button in product grid if visible
            const gridButton = document.querySelector(`.product-card button[data-product-id="${product.product_id}"]`);
            if (gridButton) {
                gridButton.classList.remove('selected');
                gridButton.textContent = 'Add to Compare';
            }
            
            // Update count and compare button
            updateSelectionStatus();
        });
        
        selectedItems.appendChild(selectedItem);
    }
    
    /**
     * Update the selection status (count and button state)
     */
    function updateSelectionStatus() {
        const count = selectedProducts.length;
        selectedCount.textContent = `(${count})`;
        
        // Enable compare button if at least 2 products are selected
        if (count >= 2) {
            compareBtn.disabled = false;
        } else {
            compareBtn.disabled = true;
        }
    }
    
    /**
     * Compare selected products
     */
    function compareProducts() {
        comparisonResult.innerHTML = '<div class="loading">Comparing products...</div>';
        
        const productIds = selectedProducts.map(product => product.product_id);
        
        fetch(`${API_BASE_URL}/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ product_ids: productIds }),
        })
            .then(response => response.json())
            .then(data => {
                renderComparisonTable(data);
            })
            .catch(error => {
                console.error('Error comparing products:', error);
                comparisonResult.innerHTML = '<div class="error">Error comparing products. Please try again.</div>';
            });
    }
    
    /**
     * Render the comparison table
     */
    function renderComparisonTable(products) {
        // Create table structure
        const table = document.createElement('table');
        table.className = 'comparison-table';
        
        // Create header row with product names
        const headerRow = document.createElement('tr');
        const emptyHeader = document.createElement('th');
        headerRow.appendChild(emptyHeader);
        
        products.forEach(product => {
            const th = document.createElement('th');
            th.textContent = product.title;
            headerRow.appendChild(th);
        });
        
        table.appendChild(headerRow);
        
        // Add product images
        const imageRow = document.createElement('tr');
        const imageLabelCell = document.createElement('td');
        imageLabelCell.textContent = 'Image';
        imageRow.appendChild(imageLabelCell);
        
        products.forEach(product => {
            const td = document.createElement('td');
            td.className = 'product-image-cell';
            
            const img = document.createElement('img');
            img.src = product.image_url || 'images/product-placeholder.png';
            img.alt = product.title;
            td.appendChild(img);
            
            imageRow.appendChild(td);
        });
        
        table.appendChild(imageRow);
        
        // Add price row
        addComparisonRow(table, products, 'Price', product => formatPrice(product.price), 'price', 'min');
        
        // Add original price row if any product has a different original price
        const hasDiscounts = products.some(p => p.original_price && p.original_price > p.price);
        if (hasDiscounts) {
            addComparisonRow(table, products, 'Original Price', product => 
                product.original_price ? formatPrice(product.original_price) : 'N/A');
            
            // Add discount percentage
            addComparisonRow(table, products, 'Discount', product => {
                if (product.original_price && product.original_price > product.price) {
                    const discountPercent = Math.round((1 - (product.price / product.original_price)) * 100);
                    return `${discountPercent}%`;
                }
                return 'N/A';
            }, 'discount', 'max');
        }
        
        // Add rating
        addComparisonRow(table, products, 'Rating', product => {
            const rating = parseFloat(product.rating) || 0;
            return `${getStarRating(rating)} (${rating.toFixed(1)})`;
        }, 'rating', 'max');
        
        // Add rating count
        addComparisonRow(table, products, 'Rating Count', product => 
            product.rating_count ? product.rating_count.toLocaleString() : '0', 'rating_count', 'max');
        
        // Add category
        addComparisonRow(table, products, 'Category', product => product.category || 'N/A');
        
        // Add brand
        addComparisonRow(table, products, 'Brand', product => product.brand || 'N/A');
        
        // Add availability
        addComparisonRow(table, products, 'Availability', product => product.availability || 'N/A');
        
        // Add link to Amazon
        const linkRow = document.createElement('tr');
        const linkLabelCell = document.createElement('td');
        linkLabelCell.textContent = 'Amazon Link';
        linkRow.appendChild(linkLabelCell);
        
        products.forEach(product => {
            const td = document.createElement('td');
            
            if (product.product_url) {
                const link = document.createElement('a');
                link.href = product.product_url;
                link.target = '_blank';
                link.textContent = 'View on Amazon';
                link.className = 'btn-primary';
                td.appendChild(link);
            } else {
                td.textContent = 'Link not available';
            }
            
            linkRow.appendChild(td);
        });
        
        table.appendChild(linkRow);
        
        // Clear previous content and add the table
        comparisonResult.innerHTML = '';
        comparisonResult.appendChild(table);
    }
    
    /**
     * Add a row to the comparison table
     */
    function addComparisonRow(table, products, label, valueFunc, compareKey = null, compareMode = null) {
        const row = document.createElement('tr');
        const labelCell = document.createElement('td');
        labelCell.textContent = label;
        row.appendChild(labelCell);
        
        // Determine winner for comparable fields
        let winnerIndex = -1;
        
        if (compareKey && compareMode) {
            const values = products.map(p => parseFloat(p[compareKey]) || 0);
            
            if (compareMode === 'min') {
                // Lower is better (e.g., price)
                const minValue = Math.min(...values.filter(v => v > 0));
                winnerIndex = values.findIndex(v => v === minValue);
            } else if (compareMode === 'max') {
                // Higher is better (e.g., rating)
                const maxValue = Math.max(...values);
                winnerIndex = values.findIndex(v => v === maxValue);
            }
        }
        
        products.forEach((product, index) => {
            const td = document.createElement('td');
            td.innerHTML = valueFunc(product);
            
            if (index === winnerIndex) {
                td.classList.add('winner');
            }
            
            row.appendChild(td);
        });
        
        table.appendChild(row);
    }
    
    /**
     * Load top deals from the API
     */
    function loadTopDeals() {
        const dealsGrid = document.getElementById('deals-grid');
        dealsGrid.innerHTML = '<div class="loading">Loading top deals...</div>';
        
        fetch(`${API_BASE_URL}/top_discounts?limit=20`)
            .then(response => response.json())
            .then(data => {
                dealsGrid.innerHTML = '';
                
                if (data.length === 0) {
                    dealsGrid.innerHTML = '<div class="no-results">No deals found at the moment.</div>';
                    return;
                }
                
                data.forEach(product => {
                    const card = productCardTemplate.content.cloneNode(true);
                    
                    // Set product image
                    const imgElement = card.querySelector('.product-image img');
                    imgElement.src = product.image_url || 'images/product-placeholder.png';
                    imgElement.alt = product.title;
                    
                    // Set product title
                    card.querySelector('.product-title').textContent = product.title;
                    
                    // Set rating stars
                    const ratingStars = card.querySelector('.rating-stars');
                    const rating = parseFloat(product.rating) || 0;
                    ratingStars.innerHTML = getStarRating(rating);
                    
                    // Set rating count
                    card.querySelector('.rating-count').textContent = 
                        `(${product.rating_count ? product.rating_count.toLocaleString() : 0})`;
                    
                    // Set prices
                    const currentPrice = card.querySelector('.current-price');
                    const originalPrice = card.querySelector('.original-price');
                    const discountBadge = card.querySelector('.discount-badge');
                    
                    currentPrice.textContent = formatPrice(product.price);
                    
                    if (product.original_price && product.original_price > product.price) {
                        originalPrice.textContent = formatPrice(product.original_price);
                        
                        // Calculate discount percentage
                        const discountPercent = Math.round((1 - (product.price / product.original_price)) * 100);
                        discountBadge.textContent = `-${discountPercent}%`;
                    } else {
                        originalPrice.style.display = 'none';
                        discountBadge.style.display = 'none';
                    }
                    
                    // Change button to "View Details"
                    const addButton = card.querySelector('.add-to-compare-btn');
                    addButton.textContent = 'View Details';
                    addButton.addEventListener('click', () => {
                        // Redirect to compare section and find this product
                        document.getElementById('nav-compare').click();
                        categoryFilter.value = product.category || '';
                        loadProducts();
                        // TODO: Scroll to this product or highlight it
                    });
                    
                    dealsGrid.appendChild(card);
                });
            })
            .catch(error => {
                console.error('Error loading deals:', error);
                dealsGrid.innerHTML = '<div class="error">Error loading deals. Please try again.</div>';
            });
    }
    
    /**
     * Handle URL parameters for direct navigation
     */
    function handleUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Check for section parameter
        const section = urlParams.get('section');
        if (section) {
            const targetNavLink = document.getElementById(`nav-${section}`);
            if (targetNavLink) {
                targetNavLink.click();
            }
        }
        
        // Check for category parameter
        const category = urlParams.get('category');
        if (category) {
            categoryFilter.value = category;
            if (section === 'compare') {
                loadProducts();
            }
        }
    }
    
    /**
     * Helper function to format price as currency
     */
    function formatPrice(price) {
        if (!price) return '$0.00';
        
        return new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(price);
    }
    
    /**
     * Helper function to generate star rating HTML
     */
    function getStarRating(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let stars = '';
        
        // Add full stars
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }
        
        // Add half star if needed
        if (halfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Add empty stars
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star"></i>';
        }
        
        return stars;
    }
});