#!/usr/bin/env python3
"""
Migration script to convert all timestamp data from local time to UTC.
This script will:
1. Convert main database (doc2dev) repositories table
2. Convert user management database (doc2dev_users) users table  
3. Convert all user-specific databases (doc2dev_user_*) repositories tables
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings

def get_database_connection(database_name: str):
    """Create database connection for given database name"""
    settings = Settings()
    db_config = settings.metadata_db.config
    connection_string = f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{database_name}"
    engine = create_engine(connection_string)
    return engine

def convert_timestamps_to_utc(engine, table_name: str, database_name: str):
    """Convert timestamp columns from local time to UTC"""
    try:
        with engine.connect() as connection:
            # Convert created_at and updated_at to UTC
            query = text(f"""
                UPDATE {table_name} 
                SET 
                    created_at = CONVERT_TZ(created_at, @@session.time_zone, '+00:00'),
                    updated_at = CONVERT_TZ(updated_at, @@session.time_zone, '+00:00')
                WHERE created_at IS NOT NULL OR updated_at IS NOT NULL
            """)
            
            result = connection.execute(query)
            connection.commit()
            
            print(f"✅ Converted {result.rowcount} records in {database_name}.{table_name}")
            
    except Exception as e:
        print(f"❌ Error converting {database_name}.{table_name}: {e}")

def get_user_databases():
    """Get list of all user-specific databases"""
    try:
        # Connect to MySQL server to list databases
        settings = Settings()
        db_config = settings.metadata_db.config
        connection_string = f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/"
        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES LIKE 'doc2dev_user_%'"))
            user_databases = [row[0] for row in result]
            
        return user_databases
        
    except Exception as e:
        print(f"❌ Error getting user databases: {e}")
        return []

def main():
    """Main migration function"""
    print("🚀 Starting UTC migration...")
    
    # 1. Convert main database (doc2dev)
    print("\n📊 Converting main database (doc2dev)...")
    try:
        engine = get_database_connection("doc2dev")
        convert_timestamps_to_utc(engine, "repositories", "doc2dev")
    except Exception as e:
        print(f"❌ Error with main database: {e}")
    
    # 2. Convert user management database (doc2dev_users)
    print("\n👥 Converting user management database (doc2dev_users)...")
    try:
        engine = get_database_connection("doc2dev_users")
        convert_timestamps_to_utc(engine, "users", "doc2dev_users")
    except Exception as e:
        print(f"❌ Error with user management database: {e}")
    
    # 3. Convert all user-specific databases
    print("\n🔄 Converting user-specific databases...")
    user_databases = get_user_databases()
    
    if not user_databases:
        print("ℹ️  No user-specific databases found.")
    else:
        print(f"📋 Found {len(user_databases)} user databases")
        
        for db_name in user_databases:
            try:
                engine = get_database_connection(db_name)
                convert_timestamps_to_utc(engine, "repositories", db_name)
            except Exception as e:
                print(f"❌ Error with {db_name}: {e}")
    
    print("\n✅ UTC migration completed!")
    print("\n⚠️  Important: After running this migration, make sure to:")
    print("   1. Deploy the updated backend code with UTC timestamp functions")
    print("   2. Restart your application servers")
    print("   3. Verify that new records are being created with UTC timestamps")

if __name__ == "__main__":
    main()
