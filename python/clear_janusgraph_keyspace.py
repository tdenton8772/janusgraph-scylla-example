#!/usr/bin/env python3
"""
Script to clear JanusGraph keyspace from ScyllaDB to start fresh
"""

from ecommerce.services.database import db_manager
from ecommerce.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_janusgraph_keyspace():
    """Clear JanusGraph keyspace from ScyllaDB"""
    try:
        # Connect to ScyllaDB
        db_manager.scylla.connect()
        
        logger.info("Clearing JanusGraph keyspace from ScyllaDB...")
        
        with db_manager.scylla.get_session() as session:
            # Drop the JanusGraph keyspace entirely
            drop_keyspace_query = f"DROP KEYSPACE IF EXISTS {settings.database.janusgraph_keyspace}"
            logger.info(f"Executing: {drop_keyspace_query}")
            session.execute(drop_keyspace_query)
            
            # Recreate the keyspace 
            create_keyspace_query = f"""
                CREATE KEYSPACE IF NOT EXISTS {settings.database.janusgraph_keyspace}
                WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 3}}
            """
            logger.info(f"Executing: {create_keyspace_query}")
            session.execute(create_keyspace_query)
            
            logger.info("JanusGraph keyspace cleared and recreated successfully")
                
    except Exception as e:
        logger.error(f"Failed to clear JanusGraph keyspace: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.scylla.disconnect()

if __name__ == "__main__":
    clear_janusgraph_keyspace()