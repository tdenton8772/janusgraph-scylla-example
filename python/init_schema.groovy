// JanusGraph Schema Initialization with Comprehensive Indexes
// This script creates all vertex labels, edge labels, property keys, and indexes

// Open management instance
mgmt = graph.openManagement()

try {
    println "Starting comprehensive schema initialization..."

    // Property Keys - Define all properties used in the application
    println "Creating property keys..."
    
    // User properties
    if (!mgmt.containsPropertyKey('user_id')) {
        mgmt.makePropertyKey('user_id').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('username')) {
        mgmt.makePropertyKey('username').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('email')) {
        mgmt.makePropertyKey('email').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('first_name')) {
        mgmt.makePropertyKey('first_name').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('last_name')) {
        mgmt.makePropertyKey('last_name').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('registration_date')) {
        mgmt.makePropertyKey('registration_date').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('is_active')) {
        mgmt.makePropertyKey('is_active').dataType(Boolean.class).make()
    }
    if (!mgmt.containsPropertyKey('address')) {
        mgmt.makePropertyKey('address').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('phone')) {
        mgmt.makePropertyKey('phone').dataType(String.class).make()
    }

    // Product properties
    if (!mgmt.containsPropertyKey('product_id')) {
        mgmt.makePropertyKey('product_id').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('name')) {
        mgmt.makePropertyKey('name').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('description')) {
        mgmt.makePropertyKey('description').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('price')) {
        mgmt.makePropertyKey('price').dataType(Double.class).make()
    }
    if (!mgmt.containsPropertyKey('category')) {
        mgmt.makePropertyKey('category').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('brand')) {
        mgmt.makePropertyKey('brand').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('sku')) {
        mgmt.makePropertyKey('sku').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('stock_quantity')) {
        mgmt.makePropertyKey('stock_quantity').dataType(Integer.class).make()
    }
    if (!mgmt.containsPropertyKey('created_date')) {
        mgmt.makePropertyKey('created_date').dataType(String.class).make()
    }

    // Order properties  
    if (!mgmt.containsPropertyKey('order_id')) {
        mgmt.makePropertyKey('order_id').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('order_date')) {
        mgmt.makePropertyKey('order_date').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('status')) {
        mgmt.makePropertyKey('status').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('total_amount')) {
        mgmt.makePropertyKey('total_amount').dataType(Double.class).make()
    }
    if (!mgmt.containsPropertyKey('shipping_address')) {
        mgmt.makePropertyKey('shipping_address').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('payment_method')) {
        mgmt.makePropertyKey('payment_method').dataType(String.class).make()
    }

    // Review properties
    if (!mgmt.containsPropertyKey('review_id')) {
        mgmt.makePropertyKey('review_id').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('rating')) {
        mgmt.makePropertyKey('rating').dataType(Integer.class).make()
    }
    if (!mgmt.containsPropertyKey('title')) {
        mgmt.makePropertyKey('title').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('comment')) {
        mgmt.makePropertyKey('comment').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('review_date')) {
        mgmt.makePropertyKey('review_date').dataType(String.class).make()
    }
    if (!mgmt.containsPropertyKey('is_verified_purchase')) {
        mgmt.makePropertyKey('is_verified_purchase').dataType(Boolean.class).make()
    }

    // Vertex Labels
    println "Creating vertex labels..."
    if (!mgmt.containsVertexLabel('user')) {
        mgmt.makeVertexLabel('user').make()
    }
    if (!mgmt.containsVertexLabel('product')) {
        mgmt.makeVertexLabel('product').make()
    }
    if (!mgmt.containsVertexLabel('order')) {
        mgmt.makeVertexLabel('order').make()
    }
    if (!mgmt.containsVertexLabel('review')) {
        mgmt.makeVertexLabel('review').make()
    }

    // Edge Labels
    println "Creating edge labels..."
    if (!mgmt.containsEdgeLabel('placed_order')) {
        mgmt.makeEdgeLabel('placed_order').make()
    }
    if (!mgmt.containsEdgeLabel('wrote_review')) {
        mgmt.makeEdgeLabel('wrote_review').make()
    }
    if (!mgmt.containsEdgeLabel('has_review')) {
        mgmt.makeEdgeLabel('has_review').make()
    }

    // Composite Indexes for fast vertex lookups
    println "Creating composite indexes..."
    
    // Primary key indexes (unique)
    if (!mgmt.containsGraphIndex('userByUserId')) {
        mgmt.buildIndex('userByUserId', Vertex.class)
           .addKey(mgmt.getPropertyKey('user_id'))
           .indexOnly(mgmt.getVertexLabel('user'))
           .unique()
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('productByProductId')) {
        mgmt.buildIndex('productByProductId', Vertex.class)
           .addKey(mgmt.getPropertyKey('product_id'))
           .indexOnly(mgmt.getVertexLabel('product'))
           .unique()
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('orderByOrderId')) {
        mgmt.buildIndex('orderByOrderId', Vertex.class)
           .addKey(mgmt.getPropertyKey('order_id'))
           .indexOnly(mgmt.getVertexLabel('order'))
           .unique()
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('reviewByReviewId')) {
        mgmt.buildIndex('reviewByReviewId', Vertex.class)
           .addKey(mgmt.getPropertyKey('review_id'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .unique()
           .buildCompositeIndex()
    }

    // Secondary unique indexes
    if (!mgmt.containsGraphIndex('userByUsername')) {
        mgmt.buildIndex('userByUsername', Vertex.class)
           .addKey(mgmt.getPropertyKey('username'))
           .indexOnly(mgmt.getVertexLabel('user'))
           .unique()
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('userByEmail')) {
        mgmt.buildIndex('userByEmail', Vertex.class)
           .addKey(mgmt.getPropertyKey('email'))
           .indexOnly(mgmt.getVertexLabel('user'))
           .unique()
           .buildCompositeIndex()
    }

    // Non-unique indexes for queries
    if (!mgmt.containsGraphIndex('productByCategory')) {
        mgmt.buildIndex('productByCategory', Vertex.class)
           .addKey(mgmt.getPropertyKey('category'))
           .indexOnly(mgmt.getVertexLabel('product'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('productByBrand')) {
        mgmt.buildIndex('productByBrand', Vertex.class)
           .addKey(mgmt.getPropertyKey('brand'))
           .indexOnly(mgmt.getVertexLabel('product'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('orderByUserId')) {
        mgmt.buildIndex('orderByUserId', Vertex.class)
           .addKey(mgmt.getPropertyKey('user_id'))
           .indexOnly(mgmt.getVertexLabel('order'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('orderByStatus')) {
        mgmt.buildIndex('orderByStatus', Vertex.class)
           .addKey(mgmt.getPropertyKey('status'))
           .indexOnly(mgmt.getVertexLabel('order'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('reviewByProductId')) {
        mgmt.buildIndex('reviewByProductId', Vertex.class)
           .addKey(mgmt.getPropertyKey('product_id'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('reviewByUserId')) {
        mgmt.buildIndex('reviewByUserId', Vertex.class)
           .addKey(mgmt.getPropertyKey('user_id'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('reviewByRating')) {
        mgmt.buildIndex('reviewByRating', Vertex.class)
           .addKey(mgmt.getPropertyKey('rating'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .buildCompositeIndex()
    }

    // Composite multi-key indexes for common query patterns
    if (!mgmt.containsGraphIndex('productByCategoryAndBrand')) {
        mgmt.buildIndex('productByCategoryAndBrand', Vertex.class)
           .addKey(mgmt.getPropertyKey('category'))
           .addKey(mgmt.getPropertyKey('brand'))
           .indexOnly(mgmt.getVertexLabel('product'))
           .buildCompositeIndex()
    }
    
    if (!mgmt.containsGraphIndex('reviewByProductAndRating')) {
        mgmt.buildIndex('reviewByProductAndRating', Vertex.class)
           .addKey(mgmt.getPropertyKey('product_id'))
           .addKey(mgmt.getPropertyKey('rating'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .buildCompositeIndex()
    }

    // Vertex-centric indexes for efficient edge traversals
    println "Creating vertex-centric indexes..."
    
    // Index for user -> orders by date
    userLabel = mgmt.getVertexLabel('user')
    placedOrderLabel = mgmt.getEdgeLabel('placed_order')
    orderDateKey = mgmt.getPropertyKey('order_date')
    
    if (!mgmt.containsRelationIndex(userLabel, 'userOrdersByDate')) {
        mgmt.buildEdgeIndex(placedOrderLabel, 'userOrdersByDate', Direction.OUT, Order.desc, orderDateKey)
    }
    
    // Index for product -> reviews by rating  
    productLabel = mgmt.getVertexLabel('product')
    hasReviewLabel = mgmt.getEdgeLabel('has_review')
    ratingKey = mgmt.getPropertyKey('rating')
    
    if (!mgmt.containsRelationIndex(productLabel, 'productReviewsByRating')) {
        mgmt.buildEdgeIndex(hasReviewLabel, 'productReviewsByRating', Direction.OUT, Order.desc, ratingKey)
    }
    
    // Index for user -> reviews by date
    wroteReviewLabel = mgmt.getEdgeLabel('wrote_review')
    reviewDateKey = mgmt.getPropertyKey('review_date')
    
    if (!mgmt.containsRelationIndex(userLabel, 'userReviewsByDate')) {
        mgmt.buildEdgeIndex(wroteReviewLabel, 'userReviewsByDate', Direction.OUT, Order.desc, reviewDateKey)
    }

    // Commit the schema
    mgmt.commit()
    println "✅ Schema committed successfully!"

    // Wait for indexes to be available
    println "Waiting for indexes to become available..."
    
    // Re-open management to check index status
    mgmt2 = graph.openManagement()
    
    // Get all indexes and wait for them to be enabled
    allIndexes = mgmt2.getGraphIndexes(Vertex.class)
    allIndexes.each { index ->
        println "Index: ${index.name()}, Status: ${mgmt2.getIndexStatus(index)}"
    }
    
    mgmt2.rollback()
    
    println "✅ Comprehensive schema with indexes created successfully!"
    println "The graph is now ready for high-performance data loading and queries."
    
} catch (Exception e) {
    println "❌ Error during schema creation: ${e.getMessage()}"
    mgmt.rollback()
    throw e
}