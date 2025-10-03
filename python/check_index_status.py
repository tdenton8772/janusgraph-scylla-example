#!/usr/bin/env python3

import time
import logging
from gremlin_python.driver import client
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_index_status():
    """Check the status of all JanusGraph indexes"""
    # Connect to JanusGraph
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info("Checking index status...")
        
        # Get detailed index status
        status_script = """
mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    result = [:]
    
    indexes.each { index ->
        indexName = index.name()
        result[indexName] = [:]
        
        // Get the property keys for this index
        result[indexName]['keys'] = []
        index.getFieldKeys().each { key ->
            result[indexName]['keys'] << key.name()
        }
        
        // Get the index status for each property key
        result[indexName]['status'] = [:]
        index.getFieldKeys().each { key ->
            try {
                status = mgmt.getIndexStatus(index, key)
                result[indexName]['status'][key.name()] = status.toString()
            } catch (Exception e) {
                result[indexName]['status'][key.name()] = "Error: " + e.getMessage()
            }
        }
        
        // Get overall index state
        try {
            result[indexName]['state'] = index.getIndexStatus().toString()
        } catch (Exception e) {
            result[indexName]['state'] = "Unknown"
        }
    }
    
    mgmt.rollback()
    result
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        status_result = gremlin_client.submit(status_script).all().result()
        logger.info("Index status details:")
        for result in status_result:
            for index_name, details in result.items():
                logger.info(f"Index: {index_name}")
                logger.info(f"  Keys: {details.get('keys', [])}")
                logger.info(f"  State: {details.get('state', 'Unknown')}")
                logger.info(f"  Status per key: {details.get('status', {})}")
                logger.info("---")
        
        # Also try simpler approach
        simple_script = """
mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    result = []
    
    indexes.each { index ->
        result << [
            'name': index.name(),
            'indexStatus': index.getIndexStatus().toString(),
            'isComposite': index.isCompositeIndex(),
            'isMixed': index.isMixedIndex()
        ]
    }
    
    mgmt.rollback()
    result
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        logger.info("Simple index check:")
        simple_result = gremlin_client.submit(simple_script).all().result()
        for result in simple_result:
            for index_info in result:
                logger.info(f"Index: {index_info['name']}")
                logger.info(f"  Status: {index_info['indexStatus']}")
                logger.info(f"  Composite: {index_info['isComposite']}")
                logger.info(f"  Mixed: {index_info['isMixed']}")
                logger.info("---")
        
    except Exception as e:
        logger.error(f"Failed to check index status: {e}")
        raise
    finally:
        gremlin_client.close()


def wait_for_indexes_enabled(timeout_seconds=300):
    """Wait for all indexes to become ENABLED"""
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info(f"Waiting for indexes to become ENABLED (timeout: {timeout_seconds}s)...")
        
        wait_script = """
import org.janusgraph.core.schema.SchemaStatus

mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    allEnabled = true
    statusReport = [:]
    
    indexes.each { index ->
        indexName = index.name()
        
        // For composite indexes, check if they're enabled
        if (index.isCompositeIndex()) {
            // Check the first property key status (composite indexes have uniform status)
            if (index.getFieldKeys().size() > 0) {
                firstKey = index.getFieldKeys()[0]
                status = mgmt.getIndexStatus(index, firstKey)
                statusReport[indexName] = status.toString()
                
                if (status != SchemaStatus.ENABLED) {
                    allEnabled = false
                }
            }
        }
    }
    
    mgmt.rollback()
    
    [
        'allEnabled': allEnabled,
        'statuses': statusReport
    ]
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                result = gremlin_client.submit(wait_script).all().result()[0]
                
                logger.info(f"Index statuses: {result['statuses']}")
                
                if result['allEnabled']:
                    logger.info("✅ All indexes are now ENABLED!")
                    return True
                else:
                    logger.info("Some indexes are still not enabled. Waiting...")
                    time.sleep(5)
                    
            except Exception as e:
                logger.warning(f"Error checking status: {e}. Retrying...")
                time.sleep(5)
        
        logger.warning(f"Timeout reached ({timeout_seconds}s). Some indexes may not be enabled yet.")
        return False
        
    except Exception as e:
        logger.error(f"Failed to wait for indexes: {e}")
        raise
    finally:
        gremlin_client.close()


def enable_indexes():
    """Force enable all indexes that are INSTALLED or REGISTERED"""
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info("Attempting to enable indexes...")
        
        enable_script = """
import org.janusgraph.core.schema.SchemaStatus

mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    enabledIndexes = []
    
    indexes.each { index ->
        indexName = index.name()
        
        if (index.isCompositeIndex()) {
            // For composite indexes, try to enable them
            if (index.getFieldKeys().size() > 0) {
                firstKey = index.getFieldKeys()[0]
                status = mgmt.getIndexStatus(index, firstKey)
                
                if (status == SchemaStatus.INSTALLED || status == SchemaStatus.REGISTERED) {
                    try {
                        mgmt.updateIndex(mgmt.getGraphIndex(indexName), SchemaAction.ENABLE_INDEX).get()
                        enabledIndexes << indexName
                    } catch (Exception e) {
                        // Index might already be in transition
                        println "Could not enable index " + indexName + ": " + e.getMessage()
                    }
                }
            }
        }
    }
    
    mgmt.commit()
    enabledIndexes
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        result = gremlin_client.submit(enable_script).all().result()
        logger.info(f"Attempted to enable indexes: {result}")
        
    except Exception as e:
        logger.error(f"Failed to enable indexes: {e}")
        raise
    finally:
        gremlin_client.close()


if __name__ == "__main__":
    # First, check current status
    check_index_status()
    
    # Try to enable indexes if needed
    enable_indexes()
    
    # Wait for them to become enabled
    wait_for_indexes_enabled()
    
    # Final status check
    check_index_status()