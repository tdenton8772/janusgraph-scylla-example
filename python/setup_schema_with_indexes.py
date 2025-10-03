#!/usr/bin/env python3
"""
Setup JanusGraph schema with comprehensive indexes for optimal performance.
This script will:
1. Clear existing graph data 
2. Initialize schema with vertex/edge labels and property keys
3. Create composite indexes for fast lookups
4. Create vertex-centric indexes for efficient traversals
5. Wait for indexes to become available
"""

import sys
import logging
from ecommerce.services.database import db_manager
from ecommerce.queries.graph_queries import graph_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_graph_data():
    """Clear all existing vertices and edges from the graph."""
    logger.info("Clearing existing graph data...")
    try:
        with db_manager.janusgraph.get_traversal() as g:
            # Drop all edges first to avoid constraint violations
            edge_count = g.E().count().next()
            logger.info(f"Found {edge_count} edges to remove")
            if edge_count > 0:
                g.E().drop().iterate()
                logger.info("Dropped all edges")
            
            # Then drop all vertices
            vertex_count = g.V().count().next()
            logger.info(f"Found {vertex_count} vertices to remove")
            if vertex_count > 0:
                g.V().drop().iterate()
                logger.info("Dropped all vertices")
                
        logger.info("Graph data cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to clear graph data: {e}")
        return False

def verify_clean_state():
    """Verify the graph is empty."""
    logger.info("Verifying clean graph state...")
    try:
        with db_manager.janusgraph.get_traversal() as g:
            vertex_count = g.V().count().next()
            edge_count = g.E().count().next()
            
            logger.info(f"Vertices: {vertex_count}, Edges: {edge_count}")
            
            if vertex_count == 0 and edge_count == 0:
                logger.info("✓ Graph is empty and ready for schema setup")
                return True
            else:
                logger.warning("⚠ Graph still contains data")
                return False
                
    except Exception as e:
        logger.error(f"Failed to verify clean state: {e}")
        return False

def main():
    """Main setup process."""
    try:
        logger.info("Starting JanusGraph schema setup with comprehensive indexing...")
        logger.info("Skipping data clearing - adding indexes to existing data...")
            
        # Step 3: Initialize schema with indexes
        logger.info("Initializing schema with comprehensive indexes...")
        graph_service.initialize_schema()
        
        # Step 4: Check index status
        logger.info("Checking index status...")
        graph_service.get_index_status()
        
        # Step 5: Wait for indexes to become available (optional but recommended)
        logger.info("Waiting for indexes to become fully available...")
        if graph_service.wait_for_index_availability(timeout_seconds=120):
            logger.info("✓ All indexes are ready for optimal query performance")
        else:
            logger.warning("⚠ Some indexes may still be building in the background")
        
        # Step 6: Final verification
        logger.info("Verifying final schema state...")
        with db_manager.janusgraph.get_traversal() as g:
            vertex_count = g.V().count().next()
            edge_count = g.E().count().next()
            logger.info(f"Final state - Vertices: {vertex_count}, Edges: {edge_count}")
        
        logger.info("✅ Schema setup with indexes completed successfully!")
        logger.info("The graph is now ready for high-performance data loading and queries.")
        
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Schema setup failed: {e}")
        sys.exit(1)
    finally:
        # Clean up connections
        try:
            db_manager.janusgraph.close()
        except:
            pass

if __name__ == "__main__":
    main()