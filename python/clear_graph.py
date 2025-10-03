#!/usr/bin/env python3
"""
Script to clear all vertices and edges from JanusGraph
"""

from ecommerce.services.database import db_manager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_graph():
    """Clear all vertices and edges from the graph"""
    try:
        # Connect to JanusGraph
        db_manager.janusgraph.connect()
        
        logger.info("Clearing all graph data...")
        
        with db_manager.janusgraph.get_traversal() as g:
            # Get current count
            try:
                count = g.V().count().next()
                logger.info(f"Current vertex count: {count}")
            except Exception as e:
                logger.warning(f"Could not get vertex count: {e}")
            
            # Drop all vertices (this also removes edges)
            logger.info("Dropping all vertices...")
            g.V().drop().iterate()
            
            logger.info("Graph cleared successfully")
            
            # Verify
            try:
                count = g.V().count().next()
                logger.info(f"New vertex count: {count}")
            except Exception as e:
                logger.warning(f"Could not verify vertex count: {e}")
                
    except Exception as e:
        logger.error(f"Failed to clear graph: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.janusgraph.disconnect()

if __name__ == "__main__":
    clear_graph()