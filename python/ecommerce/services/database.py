"""
Database connection services for JanusGraph and ScyllaDB.
"""

import logging
import ssl
from typing import Optional, Dict, Any
from contextlib import contextmanager

from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.cluster import Session

from gremlin_python.driver import client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversalSource
from janusgraph_python.driver.serializer import JanusGraphSONSerializersV3d0

from ..config import settings

logger = logging.getLogger(__name__)


class ScyllaDBConnection:
    """Manages connection to ScyllaDB for direct CQL operations."""
    
    def __init__(self):
        self.cluster = None
        self.session = None
        
    def connect(self) -> Session:
        """Establish shard-aware connection to ScyllaDB."""
        if self.session:
            return self.session
            
        try:
            # Set up authentication if credentials are provided
            auth_provider = None
            if settings.database.username and settings.database.password:
                auth_provider = PlainTextAuthProvider(
                    username=settings.database.username,
                    password=settings.database.password
                )
            
            # Configure SSL if enabled
            ssl_context = None
            if settings.database.ssl_enabled:
                ssl_context = ssl.create_default_context()
                if settings.database.ssl_cert_path:
                    ssl_context.load_cert_chain(settings.database.ssl_cert_path)
            
            # Create cluster connection with ScyllaDB cloud optimizations
            if settings.is_cloud_scylla:
                # Use TokenAware policy for ScyllaDB cloud
                from cassandra import ConsistencyLevel
                profile = ExecutionProfile(
                    load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc='AWS_US_EAST_1')),
                    consistency_level=ConsistencyLevel.LOCAL_QUORUM
                )
                
                # For ScyllaDB cloud, use all contact points
                contact_points = [
                    "node-0.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud",
                    "node-1.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud", 
                    "node-2.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud"
                ]
                
                self.cluster = Cluster(
                    execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                    contact_points=contact_points,
                    port=settings.database.port,
                    auth_provider=auth_provider,
                    connect_timeout=settings.database.connection_timeout,
                    protocol_version=4,
                )
            else:
                # Local development configuration
                self.cluster = Cluster(
                    [settings.database.host],
                    port=settings.database.port,
                    auth_provider=auth_provider,
                    ssl_context=ssl_context,
                    load_balancing_policy=DCAwareRoundRobinPolicy(),
                    connect_timeout=settings.database.connection_timeout,
                    protocol_version=4,
                    compression='lz4',
                )
            
            self.session = self.cluster.connect()
            
            # Enable shard-aware routing for better performance
            if not settings.is_cloud_scylla:
                self.session.default_consistency_level = 'LOCAL_QUORUM'
            
            logger.info(f"Connected to ScyllaDB at {settings.database.host}:{settings.database.port} (shard-aware)")
            
            return self.session
            
        except Exception as e:
            logger.error(f"Failed to connect to ScyllaDB: {e}")
            raise
    
    def disconnect(self):
        """Close ScyllaDB connection."""
        if self.session:
            self.session.shutdown()
            self.session = None
        if self.cluster:
            self.cluster.shutdown()
            self.cluster = None
        logger.info("Disconnected from ScyllaDB")
    
    @contextmanager
    def get_session(self):
        """Context manager for ScyllaDB session."""
        session = self.connect()
        try:
            yield session
        finally:
            # Session cleanup is handled by disconnect()
            pass


class JanusGraphConnection:
    """Manages connection to JanusGraph via Gremlin."""
    
    def __init__(self):
        self.connection = None
        self.g = None
        
    def connect(self) -> GraphTraversalSource:
        """Establish connection to JanusGraph via Gremlin."""
        if self.g:
            return self.g
            
        try:
            # Create remote connection to Gremlin server with JanusGraph serializer
            self.connection = DriverRemoteConnection(
                settings.janusgraph.gremlin_url,
                'g',
                max_workers=settings.janusgraph.max_workers,
                message_serializer=JanusGraphSONSerializersV3d0()
            )
            
            # Create graph traversal source
            self.g = traversal().withRemote(self.connection)
            
            logger.info(f"Connected to JanusGraph at {settings.janusgraph.gremlin_url}")
            return self.g
            
        except Exception as e:
            logger.error(f"Failed to connect to JanusGraph: {e}")
            raise
    
    def disconnect(self):
        """Close JanusGraph connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.g = None
        logger.info("Disconnected from JanusGraph")
    
    @contextmanager
    def get_traversal(self):
        """Context manager for graph traversal source."""
        g = self.connect()
        try:
            yield g
        finally:
            # Connection cleanup is handled by disconnect()
            pass


class DatabaseManager:
    """Manages both ScyllaDB and JanusGraph connections."""
    
    def __init__(self):
        self.scylla = ScyllaDBConnection()
        self.janusgraph = JanusGraphConnection()
        
    def connect_all(self):
        """Connect to both databases."""
        self.scylla.connect()
        self.janusgraph.connect()
        
    def disconnect_all(self):
        """Disconnect from both databases."""
        self.scylla.disconnect()
        self.janusgraph.disconnect()
        
    def setup_keyspaces(self):
        """Create necessary keyspaces if they don't exist."""
        with self.scylla.get_session() as session:
            # Create JanusGraph keyspace (usually handled by JanusGraph itself)
            create_janusgraph_keyspace = f"""
                CREATE KEYSPACE IF NOT EXISTS {settings.database.janusgraph_keyspace}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 3}}
            """
            
            # Create e-commerce keyspace for direct CQL access
            create_ecommerce_keyspace = f"""
                CREATE KEYSPACE IF NOT EXISTS {settings.database.ecommerce_keyspace}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 3}}
            """
            
            try:
                session.execute(create_janusgraph_keyspace)
                session.execute(create_ecommerce_keyspace)
                logger.info(f"Created keyspaces: {settings.database.janusgraph_keyspace}, {settings.database.ecommerce_keyspace}")
            except Exception as e:
                logger.warning(f"Could not create keyspaces (may already exist): {e}")
    
    def setup_cql_schema(self):
        """Create CQL tables for direct access patterns."""
        with self.scylla.get_session() as session:
            # Use the ecommerce keyspace
            session.execute("USE " + settings.database.ecommerce_keyspace)
            
            # Load and execute schema from schema.cql file
            import os
            schema_file = os.path.join(os.path.dirname(__file__), '../../..', 'src/main/resources/schema.cql')
            
            # For now, create tables directly here
            tables = [
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY,
                    username TEXT,
                    email TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    date_of_birth DATE,
                    registration_date TIMESTAMP,
                    is_active BOOLEAN,
                    address TEXT,
                    phone TEXT
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id UUID PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    price DECIMAL,
                    category TEXT,
                    brand TEXT,
                    sku TEXT,
                    stock_quantity INT,
                    created_date TIMESTAMP,
                    is_active BOOLEAN
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id UUID PRIMARY KEY,
                    user_id UUID,
                    order_date TIMESTAMP,
                    status TEXT,
                    total_amount DECIMAL,
                    shipping_address TEXT,
                    payment_method TEXT
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id UUID,
                    product_id UUID,
                    quantity INT,
                    unit_price DECIMAL,
                    PRIMARY KEY (order_id, product_id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    product_id UUID,
                    review_id UUID,
                    user_id UUID,
                    rating INT,
                    title TEXT,
                    comment TEXT,
                    review_date TIMESTAMP,
                    is_verified_purchase BOOLEAN,
                    PRIMARY KEY (product_id, review_id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS user_orders (
                    user_id UUID,
                    order_id UUID,
                    order_date TIMESTAMP,
                    status TEXT,
                    total_amount DECIMAL,
                    PRIMARY KEY (user_id, order_date, order_id)
                ) WITH CLUSTERING ORDER BY (order_date DESC)
                """,
                """
                CREATE TABLE IF NOT EXISTS products_by_category (
                    category TEXT,
                    product_id UUID,
                    name TEXT,
                    price DECIMAL,
                    brand TEXT,
                    created_date TIMESTAMP,
                    PRIMARY KEY (category, created_date, product_id)
                ) WITH CLUSTERING ORDER BY (created_date DESC)
                """,
                """
                CREATE TABLE IF NOT EXISTS user_reviews (
                    user_id UUID,
                    review_id UUID,
                    product_id UUID,
                    rating INT,
                    title TEXT,
                    review_date TIMESTAMP,
                    PRIMARY KEY (user_id, review_date, review_id)
                ) WITH CLUSTERING ORDER BY (review_date DESC)
                """
            ]
            
            for table_sql in tables:
                try:
                    session.execute(table_sql)
                    logger.info(f"Created table successfully")
                except Exception as e:
                    logger.warning(f"Could not create table (may already exist): {e}")
    
    @contextmanager
    def get_connections(self):
        """Context manager for both database connections."""
        try:
            self.connect_all()
            yield self.scylla.session, self.janusgraph.g
        finally:
            self.disconnect_all()


# Global database manager instance
db_manager = DatabaseManager()