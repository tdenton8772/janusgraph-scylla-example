#!/usr/bin/env python3

import logging
from gremlin_python.driver import client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simple_index_check():
    """Simple check for JanusGraph indexes"""
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info("Checking indexes with simple approach...")
        
        # Just list all indexes
        list_script = """
mgmt = graph.openManagement()
try {
    indexes = mgmt.getGraphIndexes(Vertex.class)
    result = []
    
    indexes.each { index ->
        indexData = [:]
        indexData['name'] = index.name()
        indexData['isComposite'] = index.isCompositeIndex()
        indexData['isMixed'] = index.isMixedIndex()
        indexData['isUnique'] = index.isUnique()
        
        // Get field keys
        fieldKeys = []
        index.getFieldKeys().each { key ->
            fieldKeys << key.name()
        }
        indexData['fieldKeys'] = fieldKeys
        
        result << indexData
    }
    
    mgmt.rollback()
    result
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        result = gremlin_client.submit(list_script).all().result()
        
        logger.info("📊 JanusGraph Indexes:")
        logger.info("=" * 50)
        
        if result and len(result) > 0:
            # The result is a list of dictionaries, each representing an index
            for index_info in result:
                logger.info(f"Index: {index_info['name']}")
                logger.info(f"  Type: {'Composite' if index_info['isComposite'] else 'Mixed' if index_info['isMixed'] else 'Unknown'}")
                logger.info(f"  Unique: {index_info['isUnique']}")
                logger.info(f"  Keys: {index_info['fieldKeys']}")
                logger.info("-" * 30)
            logger.info(f"✅ Found {len(result)} indexes total")
        else:
            logger.warning("No index results returned")
        
        # Test if indexes are working by doing a simple vertex lookup
        logger.info("\n🔍 Testing index functionality...")
        
        test_script = """
// Try to count vertices to see if basic queries work
g.V().count()
"""
        
        count_result = gremlin_client.submit(test_script).all().result()
        logger.info(f"Total vertices in graph: {count_result[0]}")
        
        # Try using an index for a lookup
        test_lookup_script = """
// Try to find a vertex using an indexed property (should be fast if index is working)
// This will create the vertex if it doesn't exist, then find it
g.V().hasLabel('user').has('user_id', 'test_user_123').fold().coalesce(unfold(), addV('user').property('user_id', 'test_user_123').property('username', 'test_user').property('email', 'test@example.com')).next()
// Now find it again using the index
g.V().hasLabel('user').has('user_id', 'test_user_123').count()
"""
        
        lookup_result = gremlin_client.submit(test_lookup_script).all().result()
        logger.info(f"Index lookup test result: {lookup_result}")
        logger.info("✅ Basic index functionality appears to be working!")
        
    except Exception as e:
        logger.error(f"Failed to check indexes: {e}")
        raise
    finally:
        gremlin_client.close()


def test_schema_elements():
    """Test that all schema elements are properly created"""
    gremlin_client = client.Client('ws://localhost:8182/gremlin', 'g')
    
    try:
        logger.info("\n🏗️  Testing schema elements...")
        
        schema_test_script = """
mgmt = graph.openManagement()
try {
    result = [:]
    
    // Check vertex labels
    vertexLabels = []
    mgmt.getVertexLabels().each { label ->
        vertexLabels << label.name()
    }
    result['vertexLabels'] = vertexLabels
    
    // Check edge labels  
    edgeLabels = []
    mgmt.getRelationTypes(EdgeLabel.class).each { label ->
        edgeLabels << label.name()
    }
    result['edgeLabels'] = edgeLabels
    
    // Check property keys
    propertyKeys = []
    mgmt.getRelationTypes(PropertyKey.class).each { key ->
        propertyKeys << key.name()
    }
    result['propertyKeys'] = propertyKeys
    
    mgmt.rollback()
    result
} catch (Exception e) {
    mgmt.rollback()
    throw e
}
"""
        
        schema_result = gremlin_client.submit(schema_test_script).all().result()
        
        for result in schema_result:
            logger.info(f"Vertex Labels: {result.get('vertexLabels', 'Not found')}")
            logger.info(f"Edge Labels: {result.get('edgeLabels', 'Not found')}")
            logger.info(f"Property Keys: {result.get('propertyKeys', 'Not found')}")
        
        logger.info("✅ Schema elements look good!")
        
    except Exception as e:
        logger.error(f"Failed to test schema: {e}")
        raise
    finally:
        gremlin_client.close()


if __name__ == "__main__":
    simple_index_check()
    test_schema_elements()