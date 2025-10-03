#!/usr/bin/python
#
# A simple example of connecting to a cluster
# To install the driver Run pip install scylla-driver
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.auth import PlainTextAuthProvider


def getCluster():
    profile = ExecutionProfile(load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc='AWS_US_EAST_1')))

    return Cluster(
        execution_profiles={EXEC_PROFILE_DEFAULT: profile},
        contact_points=[
            "node-0.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud", 
            "node-1.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud", 
            "node-2.aws-us-east-1.ea3501477d8a0916be9c.clusters.scylla.cloud"
        ],
        port=9042,
        auth_provider = PlainTextAuthProvider(username='scylla', password='dmcsNGSF50e9KCD'))

print('Connecting to cluster')
cluster = getCluster()
session = cluster.connect()

print('Connected to cluster %s' % cluster.metadata.cluster_name)

print('Getting metadata')
for host in cluster.metadata.all_hosts():
    print('Datacenter: %s; Host: %s; Rack: %s' % (host.datacenter, host.address, host.rack))

# Test basic functionality
print("\nTesting basic queries...")
result = session.execute("SELECT release_version FROM system.local")
version = result.one().release_version
print(f"ScyllaDB version: {version}")

# Test keyspace creation
keyspace_name = "test_connectivity"
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
    WITH replication = {{'class': 'NetworkTopologyStrategy', 'AWS_US_EAST_1': 3}}
""")
print(f"Keyspace '{keyspace_name}' created/verified")

cluster.shutdown()
print("Connection closed successfully")