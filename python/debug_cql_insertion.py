#!/usr/bin/env python3

import logging
from ecommerce.services.data_generator import data_generator
from ecommerce.queries.cql_queries import cql_service
from ecommerce.services.database import db_manager
from ecommerce.config import settings

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_cql_insertion():
    """Debug CQL insertion issues"""
    
    try:
        # Connect to database
        db_manager.connect_all()
        db_manager.setup_keyspaces()
        db_manager.setup_cql_schema()
        
        # Generate a single test user
        users = data_generator.generate_users(1)
        user = users[0]
        
        print(f"Generated test user: {user}")
        print(f"User fields:")
        print(f"  user_id: {user.user_id} ({type(user.user_id)})")
        print(f"  username: {user.username} ({type(user.username)})")
        print(f"  email: {user.email} ({type(user.email)})")
        print(f"  first_name: {user.first_name} ({type(user.first_name)})")
        print(f"  last_name: {user.last_name} ({type(user.last_name)})")
        print(f"  date_of_birth: {user.date_of_birth} ({type(user.date_of_birth)})")
        print(f"  registration_date: {user.registration_date} ({type(user.registration_date)})")
        print(f"  is_active: {user.is_active} ({type(user.is_active)})")
        print(f"  address: {user.address} ({type(user.address)})")
        print(f"  phone: {user.phone} ({type(user.phone)})")
        
        # Test manual parameter creation
        params = [
            user.user_id, user.username, user.email, user.first_name, user.last_name,
            user.date_of_birth, user.registration_date, user.is_active, user.address, user.phone
        ]
        
        print(f"\nParameters to be passed:")
        for i, param in enumerate(params):
            print(f"  [{i}]: {param} ({type(param)})")
        
        print(f"\nNumber of parameters: {len(params)}")
        print(f"Expected: 10 parameters")
        
        # Try direct CQL insertion with debugging
        try:
            with db_manager.scylla.get_session() as session:
                session.execute(f"USE {settings.database.ecommerce_keyspace}")
                
                insert_query = """
                INSERT INTO users (user_id, username, email, first_name, last_name, 
                                 date_of_birth, registration_date, is_active, address, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                print(f"\nExecuting query: {insert_query}")
                print(f"With parameters: {params}")
                
                result = session.execute(insert_query, params)
                print(f"✅ Direct insertion successful: {result}")
                
        except Exception as e:
            print(f"❌ Direct insertion failed: {e}")
            print(f"Exception type: {type(e)}")
        
        # Test via service method
        print(f"\n{'='*50}")
        print(f"Testing via CQL service method...")
        success = cql_service.insert_user(user)
        print(f"Service method result: {success}")
        
    except Exception as e:
        print(f"❌ Setup or test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_manager.disconnect_all()

if __name__ == "__main__":
    debug_cql_insertion()