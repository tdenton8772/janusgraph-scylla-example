#!/usr/bin/env python3
"""
Simple test to connect to ScyllaDB cloud with SSL
"""

import ssl
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy

# Your ScyllaDB cloud credentials
SCYLLA_HOST = "node-0.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud"
SCYLLA_PORT = 9042
SCYLLA_USERNAME = "scylla"
SCYLLA_PASSWORD = "dmcsNGSF50e9KCD"

print(f"Attempting to connect to ScyllaDB cloud at {SCYLLA_HOST}:{SCYLLA_PORT}")
print(f"Username: {SCYLLA_USERNAME}")
print(f"SSL: Enabled")

try:
    # Create SSL context for cloud connection
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # For testing - in production you'd want proper cert verification

    # Set up authentication
    auth_provider = PlainTextAuthProvider(
        username=SCYLLA_USERNAME,
        password=SCYLLA_PASSWORD
    )

    # Create cluster connection
    cluster = Cluster(
        [SCYLLA_HOST],
        port=SCYLLA_PORT,
        auth_provider=auth_provider,
        ssl_context=ssl_context,
        load_balancing_policy=DCAwareRoundRobinPolicy(),
        connect_timeout=15,
        protocol_version=4
    )

    print("Connecting...")
    session = cluster.connect()
    
    print("✅ Successfully connected to ScyllaDB cloud!")
    
    # Test a simple query
    result = session.execute("SELECT release_version FROM system.local")
    version = result.one().release_version
    print(f"ScyllaDB version: {version}")
    
    # Test keyspace creation
    keyspace_name = "test_connectivity"
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 3}}
    """)
    print(f"✅ Keyspace '{keyspace_name}' created/verified")
    
    session.shutdown()
    cluster.shutdown()
    print("✅ Connection closed successfully")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()