#!/usr/bin/env python3
"""
Test script to insert a single vertex and debug the issue
"""

from ecommerce.services.database import db_manager
from ecommerce.queries.graph_queries import graph_service
from ecommerce.models import User
from datetime import datetime
import uuid
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_user_insert():
    """Test inserting a single user vertex"""
    try:
        # Connect to JanusGraph
        db_manager.janusgraph.connect()
        
        # Create a simple test user
        test_user = User(
            user_id=uuid.uuid4(),
            username="testuser123",
            email="test@example.com", 
            first_name="Test",
            last_name="User",
            registration_date=datetime.now(),
            is_active=True,
            address="123 Test St",
            phone="555-1234"
        )
        
        logger.info(f"Attempting to insert user: {test_user.username}")
        
        # Try to insert the user
        with db_manager.janusgraph.get_traversal() as g:
            # First, let's check if we can do a simple traversal
            logger.info("Testing basic traversal...")
            count = g.V().count().next()
            logger.info(f"Current vertex count: {count}")
            
            # Try to add the vertex
            logger.info("Adding vertex...")
            result = g.addV('user').property('user_id', str(test_user.user_id)).property('username', test_user.username).next()
            logger.info(f"Vertex added successfully: {result}")
            
    except Exception as e:
        logger.error(f"Failed to insert user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.janusgraph.disconnect()

if __name__ == "__main__":
    test_single_user_insert()