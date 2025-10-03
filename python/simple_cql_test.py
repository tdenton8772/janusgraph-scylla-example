#!/usr/bin/env python3

import uuid
from datetime import datetime, date
from ecommerce.services.database import db_manager
from ecommerce.config import settings

def test_simple_cql():
    """Test direct CQL with minimal setup"""
    
    try:
        # Connect manually
        db_manager.scylla.connect()
        
        with db_manager.scylla.get_session() as session:
            # Test 1: Simple query without parameters
            print("Test 1: Simple USE keyspace")
            try:
                use_query = "USE " + settings.database.ecommerce_keyspace
                print(f"Executing: {use_query}")
                session.execute(use_query)
                print("✅ USE query successful")
            except Exception as e:
                print(f"❌ USE query failed: {e}")
                
            # Test 2: Simple parameterized query
            print("\nTest 2: Simple parameterized query")
            try:
                simple_query = "SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = ?"
                result = session.execute(simple_query, ["ecommerce"])
                print(f"✅ Simple parameterized query successful: {list(result)}")
            except Exception as e:
                print(f"❌ Simple parameterized query failed: {e}")
                
            # Test 3: INSERT with literal values (no parameters)
            print("\nTest 3: INSERT with literal values")
            try:
                session.execute("USE " + settings.database.ecommerce_keyspace)
                literal_insert = f"""
                INSERT INTO users (user_id, username, email, first_name, last_name, 
                                 date_of_birth, registration_date, is_active, address, phone)
                VALUES ({uuid.uuid4()}, 'testuser', 'test@example.com', 'Test', 'User',
                        '1990-01-01', '2021-01-01 00:00:00+0000', true, 'Test Address', '123-456-7890')
                """
                print(f"Executing literal INSERT")
                session.execute(literal_insert)
                print("✅ Literal INSERT successful")
            except Exception as e:
                print(f"❌ Literal INSERT failed: {e}")
                
            # Test 4: INSERT with parameters - the problematic case
            print("\nTest 4: INSERT with parameters")
            try:
                session.execute("USE " + settings.database.ecommerce_keyspace)
                param_insert = """
                INSERT INTO users (user_id, username, email, first_name, last_name, 
                                 date_of_birth, registration_date, is_active, address, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                test_params = [
                    uuid.uuid4(),
                    'testuser2',
                    'test2@example.com',
                    'Test2',
                    'User2',
                    date(1990, 1, 1),
                    datetime(2021, 1, 1),
                    True,
                    'Test Address 2',
                    '123-456-7890'
                ]
                
                print(f"Parameters: {test_params}")
                print(f"Parameter types: {[type(p) for p in test_params]}")
                
                session.execute(param_insert, test_params)
                print("✅ Parameterized INSERT successful")
            except Exception as e:
                print(f"❌ Parameterized INSERT failed: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        db_manager.scylla.disconnect()

if __name__ == "__main__":
    test_simple_cql()