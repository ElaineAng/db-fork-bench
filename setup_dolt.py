import psycopg2
import sys

# Connection Config
DB_CONFIG = {
    "dbname": "postgres",
    "user": "root",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

def setup():
    try:
        print("🔌 Connecting to Database...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Clean Slate
        print("🧹 Cleaning up old tables...")
        cur.execute("DROP TABLE IF EXISTS customer;")
        
        # 2. Create Table (Using standard Postgres types to be safe)
        print("🔨 Creating 'customer' table...")
        cur.execute("""
            CREATE TABLE customer (
                c_id INTEGER NOT NULL,
                c_d_id INTEGER NOT NULL,
                c_w_id INTEGER NOT NULL,
                c_first VARCHAR(16),
                c_middle CHAR(2),
                c_last VARCHAR(16),
                c_street_1 VARCHAR(20),
                c_street_2 VARCHAR(20),
                c_city VARCHAR(20),
                c_state CHAR(2),
                c_zip CHAR(9),
                c_phone CHAR(16),
                c_since BIGINT,
                c_credit CHAR(2),
                c_credit_lim DECIMAL(12, 2),
                c_discount DECIMAL(4, 4),
                c_balance DECIMAL(12, 2),
                c_ytd_payment FLOAT,
                c_payment_cnt INTEGER,
                c_delivery_cnt INTEGER,
                c_data VARCHAR(500),
                PRIMARY KEY (c_id, c_d_id, c_w_id)
            );
        """)
        print("✅ Table 'customer' created successfully.")

        # 3. Insert Dummy Data (So the benchmark has something to read)
        print("📥 Inserting dummy data...")
        cur.execute("""
            INSERT INTO customer (c_id, c_d_id, c_w_id, c_first, c_last) 
            VALUES (1, 1, 1, 'John', 'Doe');
        """)
        print("✅ Dummy data inserted.")

        # 4. Test Dolt Functions (Direct SQL Test)
        print("\n🧪 Testing Dolt Functions...")
        
        # Create Branch
        branch_name = "test_branch_bench"
        print(f"   Executing: SELECT dolt_branch('{branch_name}', 'main')")
        try:
            cur.execute(f"SELECT dolt_branch('{branch_name}', 'main');")
            print("   ✅ Branch Created")
        except Exception as e:
            # Ignore if it already exists
            if "already exists" in str(e): print("   (Branch already exists)")
            else: raise e

        # Checkout Branch
        print(f"   Executing: SELECT dolt_checkout('{branch_name}')")
        cur.execute(f"SELECT dolt_checkout('{branch_name}');")
        print("   ✅ Branch Checked Out")

        # Get Current Branch
        print("   Executing: SELECT active_branch()")
        cur.execute("SELECT active_branch();")
        current = cur.fetchone()[0]
        print(f"   ✅ Current Branch: {current}")

        if current == branch_name:
            print("\n🎉 SUCCESS: Database and Dolt Logic are ready!")
        else:
            print("\n⚠️ WARNING: Branch switch didn't seem to stick.")

        conn.close()

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup()
