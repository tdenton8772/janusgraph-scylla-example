#!/usr/bin/env python3

import uuid
from datetime import datetime, date
from ecommerce.services.database import db_manager
from ecommerce.config import settings

def test_named_parameters():
    """Test using named parameters instead of positional"""
    
    try:
        db_manager.scylla.connect()
        
        with db_manager.scylla.get_session() as session:
            session.execute("USE " + settings.database.ecommerce_keyspace)
            
            # Test 1: Named parameters with INSERT
            print("Test 1: Named parameters INSERT")
            try:
                named_insert = """
                INSERT INTO users (user_id, username, email, first_name, last_name, 
                                 date_of_birth, registration_date, is_active, address, phone)
                VALUES (%(user_id)s, %(username)s, %(email)s, %(first_name)s, %(last_name)s,
                        %(date_of_birth)s, %(registration_date)s, %(is_active)s, %(address)s, %(phone)s)
                """
                
                named_params = {
                    'user_id': uuid.uuid4(),
                    'username': 'named_test',
                    'email': 'named@example.com',
                    'first_name': 'Named',
                    'last_name': 'Test',
                    'date_of_birth': date(1990, 1, 1),
                    'registration_date': datetime(2021, 1, 1),
                    'is_active': True,
                    'address': 'Named Test Address',
                    'phone': '555-1234'
                }
                
                print(f"Named parameters: {named_params}")
                session.execute(named_insert, named_params)
                print("✅ Named parameters INSERT successful")
            except Exception as e:
                print(f"❌ Named parameters INSERT failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 2: Try with prepared statement
            print("\nTest 2: Prepared statement with positional parameters")
            try:
                prepared_insert = session.prepare("""
                INSERT INTO users (user_id, username, email, first_name, last_name, 
                                 date_of_birth, registration_date, is_active, address, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """)
                
                prepared_params = [
                    uuid.uuid4(),
                    'prepared_test',
                    'prepared@example.com',
                    'Prepared',
                    'Test',
                    date(1990, 1, 1),
                    datetime(2021, 1, 1),
                    True,
                    'Prepared Test Address',
                    '555-5678'
                ]
                
                print(f"Prepared statement parameters: {prepared_params}")
                session.execute(prepared_insert, prepared_params)
                print("✅ Prepared statement INSERT successful")
            except Exception as e:
                print(f"❌ Prepared statement INSERT failed: {e}")
                import traceback
                traceback.print_exc()
                
    finally:
        db_manager.scylla.disconnect()

if __name__ == "__main__":
    test_named_parameters()