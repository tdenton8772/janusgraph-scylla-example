#!/usr/bin/env python3
"""
Create comprehensive indexes for JanusGraph using direct Groovy script submission.
This script submits Groovy commands directly to the Gremlin server to create the schema.
"""

import logging
from gremlin_python.driver.client import Client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_comprehensive_schema():
    """Create the comprehensive schema with indexes using Groovy scripts."""
    
    # Connect to the Gremlin server  
    client = Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info("Starting comprehensive schema creation...")
        
        # Submit the comprehensive schema creation script
        schema_script = """
// Open management instance
mgmt = graph.openManagement()

try {
    // Property Keys - Define all properties used in the application
    
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
    
    if (!mgmt.containsGraphIndex('reviewByProductId')) {
        mgmt.buildIndex('reviewByProductId', Vertex.class)
           .addKey(mgmt.getPropertyKey('product_id'))
           .indexOnly(mgmt.getVertexLabel('review'))
           .buildCompositeIndex()
    }

    // Commit the schema
    mgmt.commit()
    'Schema created successfully!'
    
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""

        logger.info("Submitting schema creation script...")
        result = client.submit(schema_script).all().result()
        logger.info(f"Schema creation result: {result}")
        
        # Check index status
        logger.info("Checking index status...")
        status_script = """
mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    indexStatus = [:]
    indexes.each { index ->
        statuses = mgmt.getIndexJobStatus(index)
        // Typically returns a map with property keys as keys and status as values
        indexStatus[index.name()] = statuses.toString()
    }
    mgmt.rollback()
    indexStatus
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        status_result = client.submit(status_script).all().result()
        logger.info(f"Index status: {status_result}")
        
        logger.info("✅ Comprehensive schema with indexes created successfully!")
        logger.info("The graph is now ready for high-performance data loading and queries.")
        
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    create_comprehensive_schema()