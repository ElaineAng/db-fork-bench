import psycopg2
from dblib.dolt import DoltToolSuite

# 1. Setup Connection Details
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

def test_connection():
    print("\n--- 1. Testing Connection ---")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connection Successful!")
        return conn
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

def test_table_exists(conn):
    print("\n--- 2. Checking for 'customer' table ---")
    try:
        cur = conn.cursor()
        # Query to list tables in public schema
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables found: {tables}")
        
        if 'customer' in tables:
            print("✅ 'customer' table exists.")
            # Check row count
            cur.execute("SELECT count(*) FROM customer;")
            count = cur.fetchone()[0]
            print(f"   Rows in customer: {count}")
        else:
            print("❌ 'customer' table MISSING. This is why the benchmark fails.")
            
            # ATTEMPT TO CREATE IT MANUALLY
            print("   Attempting to create it now...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer (
                  c_id int4 NOT NULL, c_d_id int2 NOT NULL, c_w_id int2 NOT NULL,
                  c_first varchar(16), c_middle bpchar(2), c_last varchar(16),
                  PRIMARY KEY (c_id, c_d_id, c_w_id)
                );
            """)
            conn.commit()
            print("   ✅ Created 'customer' table manually.")
            
    except Exception as e:
        print(f"❌ Error checking table: {e}")

def test_dolt_functions():
    print("\n--- 3. Testing Dolt Functions (The Task) ---")
    # We cheat and use the connection config directly to initialize the suite
    # We need a dummy 'bench_config' object that has a .db_config attribute
    class DummyConfig:
        def __init__(self):
            self.db_config = type('obj', (object,), {
                'host': 'localhost', 'port': 5432, 
                'dbname': 'postgres', 'username': 'postgres', 'password': 'password'
            })
            self.db_config.connect_timeout = 10

    try:
        # Initialize your Dolt class
        dolt = DoltToolSuite(DummyConfig())
        
        # Test 1: Get Current Branch
        branch, bid = dolt._get_current_branch_impl()
        print(f"✅ Current Branch: {branch} (ID: {bid})")
        
        # Test 2: Create Branch
        new_branch = "test_branch_01"
        print(f"   Creating branch '{new_branch}'...")
        dolt._create_branch_impl(new_branch, "main")
        print("✅ Branch created.")

        # Test 3: Connect (Checkout) Branch
        print(f"   Checking out '{new_branch}'...")
        dolt._connect_branch_impl(new_branch)
        
        # Verify switch
        curr, _ = dolt._get_current_branch_impl()
        if curr == new_branch:
             print(f"✅ Successfully switched to: {curr}")
        else:
             print(f"❌ Failed to switch. Still on: {curr}")
             
    except Exception as e:
        print(f"❌ Dolt Function Error: {e}")

if __name__ == "__main__":
    conn = test_connection()
    if conn:
        test_table_exists(conn)
        conn.close()
        test_dolt_functions()
