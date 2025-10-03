#!/usr/bin/env python3
"""
Debug script to check if configuration is loading properly
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

print("Environment variables:")
print(f"SCYLLA_HOST: {os.environ.get('SCYLLA_HOST', 'NOT SET')}")
print(f"SCYLLA_PORT: {os.environ.get('SCYLLA_PORT', 'NOT SET')}")
print(f"SCYLLA_USERNAME: {os.environ.get('SCYLLA_USERNAME', 'NOT SET')}")
print(f"SCYLLA_SSL_ENABLED: {os.environ.get('SCYLLA_SSL_ENABLED', 'NOT SET')}")

print("\n" + "="*50)

try:
    from ecommerce.config import settings
    print("Configuration loaded successfully!")
    print(f"Database host: {settings.database.host}")
    print(f"Database port: {settings.database.port}")
    print(f"Database username: {settings.database.username}")
    print(f"SSL enabled: {settings.database.ssl_enabled}")
    print(f"Is cloud ScyllaDB: {settings.is_cloud_scylla}")
except Exception as e:
    print(f"Error loading configuration: {e}")
    import traceback
    traceback.print_exc()