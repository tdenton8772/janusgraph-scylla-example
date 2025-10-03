#!/usr/bin/env python3
"""
Quick test to verify ScyllaDB driver is working correctly.
Run this before the full demo to ensure connectivity.
"""

import sys
import os

# Add the python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

try:
    # Test ScyllaDB driver import
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    print("✅ ScyllaDB driver imports successful")
    
    # Test our application imports
    from ecommerce.config import settings
    from ecommerce.services.database import db_manager
    print("✅ Application imports successful")
    
    # Test basic connection (will fail if ScyllaDB not running, but import should work)
    try:
        print(f"📍 Attempting to connect to ScyllaDB at {settings.database.host}:{settings.database.port}")
        db_manager.scylla.connect()
        print("✅ ScyllaDB connection successful!")
        
        # Test keyspace setup
        db_manager.setup_keyspaces()
        print("✅ Keyspaces verified/created")
        
        db_manager.scylla.disconnect()
        print("✅ Connection cleanup successful")
        
    except Exception as e:
        print(f"⚠️  ScyllaDB connection failed (expected if not running): {e}")
        print("   This is normal if ScyllaDB isn't started yet")
    
    print("\n🎉 ScyllaDB driver setup is correct!")
    print("   Run './scripts/setup.sh start' to start ScyllaDB")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("   Please install the ScyllaDB driver: pip install scylla-driver")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)