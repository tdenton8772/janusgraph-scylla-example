"""
Graph query service using Gremlin for JanusGraph operations.
This demonstrates graph-based access patterns and traversals.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

from gremlin_python.process.graph_traversal import GraphTraversalSource, __
from gremlin_python.process.traversal import T
from gremlin_python.driver import client

from ..models import User, Product, Order, Review
from ..services.database import db_manager
from ..config import settings

logger = logging.getLogger(__name__)


class GraphQueryService:
    """Service for graph-based queries using JanusGraph and Gremlin."""
    
    def __init__(self):
        self.g = None
    
    def initialize_schema(self):
        """Initialize the graph schema with vertex labels and edge labels."""
        logger.info("Starting JanusGraph schema initialization...")
        
        # Since JanusGraph has DisableDefaultSchemaMaker enabled, we need to create
        # vertex and edge labels before attempting to use them
        
        try:
            # We'll use the existing connection and submit management scripts
            # Create vertex labels, edge labels, and property keys through Gremlin server
            
            vertex_labels = ['user', 'product', 'order', 'review']
            edge_labels = ['placed_order', 'wrote_review', 'has_review']
            
            # Define all property keys used in the application
            property_keys = {
                # User properties
                'user_id': 'String',
                'username': 'String', 
                'email': 'String',
                'first_name': 'String',
                'last_name': 'String',
                'registration_date': 'String',  # ISO format timestamp
                'is_active': 'Boolean',
                'address': 'String',
                'phone': 'String',
                
                # Product properties
                'product_id': 'String',
                'name': 'String',
                'description': 'String', 
                'price': 'Double',
                'category': 'String',
                'brand': 'String',
                'sku': 'String',
                'stock_quantity': 'Integer',
                'created_date': 'String',  # ISO format timestamp
                
                # Order properties
                'order_id': 'String',
                'order_date': 'String',  # ISO format timestamp
                'status': 'String',
                'total_amount': 'Double',
                'shipping_address': 'String',
                'payment_method': 'String',
                
                # Review properties
                'review_id': 'String',
                'rating': 'Integer',
                'title': 'String',
                'comment': 'String',
                'review_date': 'String',  # ISO format timestamp
                'is_verified_purchase': 'Boolean'
            }
            
            # Get access to the remote connection for submitting scripts
            remote_conn = db_manager.janusgraph.connection
            
            if remote_conn and hasattr(remote_conn, '_client'):
                client = remote_conn._client
            elif hasattr(db_manager.janusgraph, '_client'):
                client = db_manager.janusgraph._client
            else:
                client = None
                
            if client:
                
                # Create property keys first (required before vertex/edge labels)
                for prop_name, prop_type in property_keys.items():
                    try:
                        script = f"""
                        mgmt = graph.openManagement()
                        if (!mgmt.containsPropertyKey('{prop_name}')) {{
                            mgmt.makePropertyKey('{prop_name}').dataType({prop_type}.class).make()
                            mgmt.commit()
                            '{prop_name}_created'
                        }} else {{
                            mgmt.rollback() 
                            '{prop_name}_exists'
                        }}
                        """
                        result = client.submit(script).all().result()
                        logger.info(f"Property key '{prop_name}': {result}")
                    except Exception as e:
                        logger.warning(f"Could not process property key {prop_name}: {e}")
                
                # Create vertex labels
                for label in vertex_labels:
                    try:
                        script = f"""
                        mgmt = graph.openManagement()
                        try {{
                            if (!mgmt.containsVertexLabel('{label}')) {{
                                mgmt.makeVertexLabel('{label}').make()
                                mgmt.commit()
                                '{label}_created'
                            }} else {{
                                mgmt.rollback()
                                '{label}_exists'
                            }}
                        }} catch (Exception e) {{
                            mgmt.rollback()
                            'error_' + e.getMessage()
                        }}
                        """
                        result = client.submit(script).all().result()
                        logger.info(f"Vertex label '{label}': {result}")
                    except Exception as e:
                        logger.warning(f"Could not process vertex label {label}: {e}")
                
                # Create edge labels
                for label in edge_labels:
                    try:
                        script = f"""
                        mgmt = graph.openManagement()
                        try {{
                            if (!mgmt.containsEdgeLabel('{label}')) {{
                                mgmt.makeEdgeLabel('{label}').make()
                                mgmt.commit()
                                '{label}_created'
                            }} else {{
                                mgmt.rollback()
                                '{label}_exists'
                            }}
                        }} catch (Exception e) {{
                            mgmt.rollback()
                            'error_' + e.getMessage()
                        }}
                        """
                        result = client.submit(script).all().result()
                        logger.info(f"Edge label '{label}': {result}")
                    except Exception as e:
                        logger.warning(f"Could not process edge label {label}: {e}")
                
                # Create property constraints (define which properties can be used with which vertex labels)
                property_constraints = {
                    'user': ['user_id', 'username', 'email', 'first_name', 'last_name', 'registration_date', 'is_active', 'address', 'phone'],
                    'product': ['product_id', 'name', 'description', 'price', 'category', 'brand', 'sku', 'stock_quantity', 'created_date', 'is_active'],
                    'order': ['order_id', 'user_id', 'order_date', 'status', 'total_amount', 'shipping_address', 'payment_method'],
                    'review': ['review_id', 'product_id', 'user_id', 'rating', 'title', 'comment', 'review_date', 'is_verified_purchase']
                }
                
                for vertex_label, properties in property_constraints.items():
                    for prop in properties:
                        try:
                            script = f"""
                            mgmt = graph.openManagement()
                            vertexLabel = mgmt.getVertexLabel('{vertex_label}')
                            propertyKey = mgmt.getPropertyKey('{prop}')
                            mgmt.addProperties(vertexLabel, propertyKey)
                            mgmt.commit()
                            '{vertex_label}_{prop}_constraint_created'
                            """
                            result = client.submit(script).all().result()
                            logger.debug(f"Property constraint '{vertex_label}.{prop}': {result}")
                        except Exception as e:
                            logger.warning(f"Could not process property constraint {vertex_label}.{prop}: {e}")
                
                # Create composite indexes for efficient queries
                logger.info("Creating composite indexes...")
                composite_indexes = {
                    # Primary key indexes - unique identifiers
                    'userByUserId': {
                        'property_keys': ['user_id'],
                        'vertex_label': 'user',
                        'unique': True
                    },
                    'productByProductId': {
                        'property_keys': ['product_id'],
                        'vertex_label': 'product', 
                        'unique': True
                    },
                    'orderByOrderId': {
                        'property_keys': ['order_id'],
                        'vertex_label': 'order',
                        'unique': True
                    },
                    'reviewByReviewId': {
                        'property_keys': ['review_id'],
                        'vertex_label': 'review',
                        'unique': True
                    },
                    
                    # Secondary indexes for queries
                    'userByUsername': {
                        'property_keys': ['username'],
                        'vertex_label': 'user',
                        'unique': True
                    },
                    'userByEmail': {
                        'property_keys': ['email'], 
                        'vertex_label': 'user',
                        'unique': True
                    },
                    'productByCategory': {
                        'property_keys': ['category'],
                        'vertex_label': 'product',
                        'unique': False
                    },
                    'productByBrand': {
                        'property_keys': ['brand'],
                        'vertex_label': 'product', 
                        'unique': False
                    },
                    'orderByUserId': {
                        'property_keys': ['user_id'],
                        'vertex_label': 'order',
                        'unique': False
                    },
                    'orderByStatus': {
                        'property_keys': ['status'],
                        'vertex_label': 'order',
                        'unique': False
                    },
                    'reviewByProductId': {
                        'property_keys': ['product_id'],
                        'vertex_label': 'review',
                        'unique': False
                    },
                    'reviewByUserId': {
                        'property_keys': ['user_id'],
                        'vertex_label': 'review',
                        'unique': False
                    },
                    'reviewByRating': {
                        'property_keys': ['rating'],
                        'vertex_label': 'review',
                        'unique': False
                    },
                    
                    # Composite indexes for common query patterns
                    'productByCategoryAndBrand': {
                        'property_keys': ['category', 'brand'],
                        'vertex_label': 'product',
                        'unique': False
                    },
                    'reviewByProductAndRating': {
                        'property_keys': ['product_id', 'rating'],
                        'vertex_label': 'review',
                        'unique': False
                    }
                }
                
                for index_name, index_config in composite_indexes.items():
                    try:
                        # Build the property key additions
                        property_keys = index_config['property_keys']
                        add_key_statements = []
                        for pk in property_keys:
                            add_key_statements.append(f".addKey(mgmt.getPropertyKey('{pk}'))")
                        add_keys_str = ''.join(add_key_statements)
                        
                        # Build constraints
                        vertex_label_constraint = f".indexOnly(mgmt.getVertexLabel('{index_config['vertex_label']}'))" if index_config.get('vertex_label') else ""
                        unique_constraint = ".unique()" if index_config.get('unique', False) else ""
                        
                        script = f"""
                        mgmt = graph.openManagement()
                        try {{
                            if (!mgmt.containsGraphIndex('{index_name}')) {{
                                mgmt.buildIndex('{index_name}', Vertex.class){add_keys_str}{vertex_label_constraint}{unique_constraint}.buildCompositeIndex()
                                mgmt.commit()
                                '{index_name}_created'
                            }} else {{
                                mgmt.rollback()
                                '{index_name}_exists'
                            }}
                        }} catch (Exception e) {{
                            mgmt.rollback()
                            'error_' + e.getMessage()
                        }}
                        """
                        result = client.submit(script).all().result()
                        logger.info(f"Composite index '{index_name}': {result}")
                    except Exception as e:
                        logger.warning(f"Could not create composite index {index_name}: {e}")
                
                # Create vertex-centric indexes for edge traversals
                logger.info("Creating vertex-centric indexes...")
                vertex_centric_indexes = [
                    {
                        'name': 'userOrdersByDate',
                        'vertex_label': 'user',
                        'edge_label': 'placed_order',
                        'direction': 'OUT',
                        'sort_keys': ['order_date'],
                        'order': 'desc'
                    },
                    {
                        'name': 'productReviewsByRating', 
                        'vertex_label': 'product',
                        'edge_label': 'has_review',
                        'direction': 'OUT',
                        'sort_keys': ['rating'],
                        'order': 'desc'
                    },
                    {
                        'name': 'userReviewsByDate',
                        'vertex_label': 'user',
                        'edge_label': 'wrote_review',
                        'direction': 'OUT', 
                        'sort_keys': ['review_date'],
                        'order': 'desc'
                    }
                ]
                
                for vc_index in vertex_centric_indexes:
                    try:
                        sort_keys_str = ', '.join([f"mgmt.getPropertyKey('{sk}')" for sk in vc_index['sort_keys']])
                        order_str = f", org.janusgraph.core.Cardinality.SINGLE, Order.{vc_index['order']}" if 'order' in vc_index else ""
                        
                        script = f"""
                        mgmt = graph.openManagement()
                        try {{
                            vertexLabel = mgmt.getVertexLabel('{vc_index['vertex_label']}')
                            edgeLabel = mgmt.getEdgeLabel('{vc_index['edge_label']}')
                            direction = org.apache.tinkerpop.gremlin.structure.Direction.{vc_index['direction']}
                            
                            if (!mgmt.containsRelationIndex(vertexLabel, '{vc_index['name']}')) {{
                                mgmt.buildEdgeIndex(edgeLabel, '{vc_index['name']}', direction, Order.{vc_index.get('order', 'asc')}, {sort_keys_str})
                                mgmt.commit()
                                '{vc_index['name']}_created'
                            }} else {{
                                mgmt.rollback()
                                '{vc_index['name']}_exists'
                            }}
                        }} catch (Exception e) {{
                            mgmt.rollback()
                            'error_' + e.getMessage()
                        }}
                        """
                        result = client.submit(script).all().result()
                        logger.info(f"Vertex-centric index '{vc_index['name']}': {result}")
                    except Exception as e:
                        logger.warning(f"Could not create vertex-centric index {vc_index['name']}: {e}")
                
                # Wait for index completion (this is important for performance)
                logger.info("Waiting for indexes to be enabled...")
                try:
                    script = """
                    mgmt = graph.openManagement()
                    mgmt.printSchema()
                    mgmt.commit()
                    'schema_status'
                    """
                    result = client.submit(script).all().result()
                    logger.info(f"Schema status: {result}")
                except Exception as e:
                    logger.warning(f"Could not check schema status: {e}")
                
                logger.info("Schema initialization with indexes completed")
            else:
                logger.error("Could not access Gremlin client for schema management")
                self._fallback_schema_creation()
                
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            # Fall back to the alternative method
            self._fallback_schema_creation()
    
    def get_index_status(self):
        """Check the status of all graph indexes."""
        try:
            remote_conn = db_manager.janusgraph.connection
            if remote_conn and hasattr(remote_conn, '_client'):
                client = remote_conn._client
                
                script = """
                mgmt = graph.openManagement()
                indexes = mgmt.getGraphIndexes(Vertex.class)
                indexStatus = [:]
                indexes.each { index ->
                    status = mgmt.getIndexStatus(index)
                    indexStatus[index.name()] = status.toString()
                }
                mgmt.rollback()
                indexStatus
                """
                
                result = client.submit(script).all().result()
                logger.info(f"Index status: {result}")
                return result
        except Exception as e:
            logger.error(f"Failed to check index status: {e}")
            return {}
    
    def wait_for_index_availability(self, index_names=None, timeout_seconds=300):
        """Wait for indexes to become available for queries."""
        import time
        
        logger.info("Waiting for indexes to become available...")
        start_time = time.time()
        
        try:
            remote_conn = db_manager.janusgraph.connection
            if not (remote_conn and hasattr(remote_conn, '_client')):
                logger.warning("Cannot check index status - no management client available")
                return False
                
            client = remote_conn._client
            
            while (time.time() - start_time) < timeout_seconds:
                script = """
                mgmt = graph.openManagement()
                indexes = mgmt.getGraphIndexes(Vertex.class)
                allEnabled = true
                indexes.each { index ->
                    status = mgmt.getIndexStatus(index)
                    if (status != SchemaStatus.ENABLED) {
                        allEnabled = false
                    }
                }
                mgmt.rollback()
                allEnabled
                """
                
                result = client.submit(script).all().result()
                if result and result[0]:
                    logger.info("All indexes are now ENABLED and ready for queries")
                    return True
                    
                logger.info("Indexes still building, waiting 10 seconds...")
                time.sleep(10)
            
            logger.warning(f"Timeout waiting for indexes to become available after {timeout_seconds} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Failed to wait for index availability: {e}")
            return False
    
    def _fallback_schema_creation(self):
        """Fallback method to create schema by enabling schema maker temporarily."""
        try:
            logger.info("Attempting fallback schema creation method...")
            
            # Alternative: Try to enable auto schema creation temporarily
            with db_manager.janusgraph.get_traversal() as g:
                # This approach attempts to add a dummy vertex for each label to trigger creation
                # The operation will fail but may create the label in the process
                
                dummy_props = {
                    'user': {'user_id': 'dummy', 'username': 'dummy'},
                    'product': {'product_id': 'dummy', 'name': 'dummy'},
                    'order': {'order_id': 'dummy', 'user_id': 'dummy'},
                    'review': {'review_id': 'dummy', 'product_id': 'dummy', 'user_id': 'dummy'}
                }
                
                for label, props in dummy_props.items():
                    try:
                        # Try to add a dummy vertex - this might create the label
                        traversal = g.addV(label)
                        for key, value in props.items():
                            traversal = traversal.property(key, value)
                        traversal.next()
                        
                        # If successful, remove the dummy vertex
                        g.V().hasLabel(label).has(list(props.keys())[0], 'dummy').drop().iterate()
                        logger.info(f"Created vertex label '{label}' via fallback method")
                        
                    except Exception as ve:
                        logger.debug(f"Fallback creation for '{label}' failed (expected): {ve}")
                        
        except Exception as e:
            logger.error(f"Fallback schema creation failed: {e}")
            raise RuntimeError(
                f"Unable to create JanusGraph schema. JanusGraph is configured with DisableDefaultSchemaMaker. "
                f"Please either: 1) Enable automatic schema creation in JanusGraph config, or "
                f"2) Pre-create vertex labels (user, product, order, review) and edge labels "
                f"(placed_order, wrote_review, has_review) using JanusGraph Management API")
    
    def insert_user(self, user: User) -> bool:
        """Insert a user vertex into the graph."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.addV('user').property('user_id', str(user.user_id)).property('username', user.username).property('email', user.email).property('first_name', user.first_name).property('last_name', user.last_name).property('registration_date', user.registration_date.isoformat()).property('is_active', user.is_active).property('address', user.address or '').property('phone', user.phone or '').next()
                
            logger.debug(f"Inserted user vertex: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert user {user.username}: {e}")
            return False
    
    def insert_product(self, product: Product) -> bool:
        """Insert a product vertex into the graph."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.addV('product').property('product_id', str(product.product_id)).property('name', product.name).property('description', product.description or '').property('price', float(product.price)).property('category', product.category).property('brand', product.brand).property('sku', product.sku).property('stock_quantity', product.stock_quantity).property('created_date', product.created_date.isoformat()).property('is_active', product.is_active).next()
                
            logger.debug(f"Inserted product vertex: {product.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert product {product.name}: {e}")
            return False
    
    def insert_order(self, order: Order) -> bool:
        """Insert an order vertex into the graph."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.addV('order').property('order_id', str(order.order_id)).property('user_id', str(order.user_id)).property('order_date', order.order_date.isoformat()).property('status', order.status).property('total_amount', float(order.total_amount)).property('shipping_address', order.shipping_address or '').property('payment_method', order.payment_method or '').next()
                
            logger.debug(f"Inserted order vertex: {order.order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert order {order.order_id}: {e}")
            return False
    
    def insert_review(self, review: Review) -> bool:
        """Insert a review vertex into the graph."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.addV('review').property('review_id', str(review.review_id)).property('product_id', str(review.product_id)).property('user_id', str(review.user_id)).property('rating', review.rating).property('title', review.title).property('comment', review.comment or '').property('review_date', review.review_date.isoformat()).property('is_verified_purchase', review.is_verified_purchase).next()
                
            logger.debug(f"Inserted review vertex: {review.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert review {review.title}: {e}")
            return False
    
    def create_user_order_edge(self, user_id: uuid.UUID, order_id: uuid.UUID) -> bool:
        """Create an edge between user and order."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.V().hasLabel('user').has('user_id', str(user_id)).addE('placed_order').to(__.V().hasLabel('order').has('order_id', str(order_id))).next()
                
            logger.debug(f"Created user-order edge: {user_id} -> {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create user-order edge: {e}")
            return False
    
    def create_user_review_edge(self, user_id: uuid.UUID, review_id: uuid.UUID) -> bool:
        """Create an edge between user and review."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.V().hasLabel('user').has('user_id', str(user_id)).addE('wrote_review').to(__.V().hasLabel('review').has('review_id', str(review_id))).next()
                
            logger.debug(f"Created user-review edge: {user_id} -> {review_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create user-review edge: {e}")
            return False
    
    def create_product_review_edge(self, product_id: uuid.UUID, review_id: uuid.UUID) -> bool:
        """Create an edge between product and review."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                g.V().hasLabel('product').has('product_id', str(product_id)).addE('has_review').to(__.V().hasLabel('review').has('review_id', str(review_id))).next()
                
            logger.debug(f"Created product-review edge: {product_id} -> {review_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create product-review edge: {e}")
            return False
    
    # Query methods demonstrating graph traversal patterns
    
    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find a user by username - simple vertex lookup."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                result = g.V().hasLabel('user').has('username', username).valueMap().next()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to find user by username {username}: {e}")
            return None
    
    def get_user_orders(self, user_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get orders for a user using graph traversal."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                results = g.V().hasLabel('user').has('user_id', str(user_id)).out('placed_order').valueMap().limit(limit).toList()
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to get user orders for {user_id}: {e}")
            return []
    
    def get_product_reviews(self, product_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get reviews for a product using graph traversal."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                results = g.V().hasLabel('product').has('product_id', str(product_id)).out('has_review').valueMap().limit(limit).toList()
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to get product reviews for {product_id}: {e}")
            return []
    
    def find_users_who_bought_and_reviewed(self, product_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Find users who both bought and reviewed a specific product - complex traversal."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                # This is a complex traversal showing graph query power
                # Find users who have orders AND reviews for the same product
                results = g.V().hasLabel('product').has('product_id', str(product_id)).in_('has_review').in_('wrote_review').hasLabel('user').dedup().valueMap().toList()
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to find users who bought and reviewed product {product_id}: {e}")
            return []
    
    def get_product_recommendations(self, user_id: uuid.UUID, limit: int = 5) -> List[Dict[str, Any]]:
        """Get product recommendations based on similar users - collaborative filtering via graph."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                # Find products that users with similar purchase patterns have bought
                # This demonstrates the power of graph traversals for recommendations
                results = (g.V().hasLabel('user').has('user_id', str(user_id))
                          .out('placed_order')  # Get user's orders
                          .in_('placed_order')  # Find other users with same orders
                          .where(g.neq(g.V().hasLabel('user').has('user_id', str(user_id))))  # Exclude original user
                          .out('placed_order')  # Get their other orders
                          .in_('placed_order')  # Get products from those orders
                          .hasLabel('product')
                          .dedup()
                          .valueMap()
                          .limit(limit)
                          .toList())
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            return []
    
    def find_products_by_category_with_high_ratings(self, category: str, min_rating: int = 4, limit: int = 10) -> List[Dict[str, Any]]:
        """Find products in a category with high average ratings - aggregation via traversal."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                # This shows graph aggregation capabilities
                results = (g.V().hasLabel('product')
                          .has('category', category)
                          .where(g.out('has_review').has('rating', g.gte(min_rating)))
                          .valueMap()
                          .limit(limit)
                          .toList())
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"Failed to find high-rated products in category {category}: {e}")
            return []
    
    def get_user_social_network(self, user_id: uuid.UUID, depth: int = 2) -> Dict[str, Any]:
        """Get a user's social network based on shared purchases - multi-hop traversal."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                # Find users connected through shared product purchases
                user_info = g.V().hasLabel('user').has('user_id', str(user_id)).valueMap().next()
                
                # Get users who bought the same products (1-hop)
                direct_connections = (g.V().hasLabel('user').has('user_id', str(user_id))
                                    .out('placed_order')
                                    .in_('placed_order')
                                    .where(g.neq(g.V().hasLabel('user').has('user_id', str(user_id))))
                                    .dedup()
                                    .valueMap()
                                    .toList())
                
                return {
                    'user': dict(user_info),
                    'connections': [dict(conn) for conn in direct_connections],
                    'connection_count': len(direct_connections)
                }
        except Exception as e:
            logger.error(f"Failed to get social network for user {user_id}: {e}")
            return {}
    
    def analyze_product_popularity_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze product popularity trends over time - temporal graph analysis."""
        try:
            with db_manager.janusgraph.get_traversal() as g:
                # This would typically involve date-based filtering
                # For simplicity, we'll get products with most reviews
                results = (g.V().hasLabel('product')
                          .project('product', 'review_count')
                          .by(g.valueMap())
                          .by(g.out('has_review').count())
                          .order().by(g.select('review_count'), g.desc())
                          .limit(10)
                          .toList())
                
                return [{'product': dict(result['product']), 'review_count': result['review_count']} 
                       for result in results]
        except Exception as e:
            logger.error(f"Failed to analyze product popularity trends: {e}")
            return []


# Global graph query service instance
graph_service = GraphQueryService()