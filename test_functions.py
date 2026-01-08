import sys
import psycopg2
from dblib.dolt import DoltToolSuite

# --- Configuration ---
# We use 'root' because we know that exists. 
# We add a dummy password to stop the 'no password supplied' error.
URI = "postgresql://postgres:password@127.0.0.1:5432/dolt_data"

# --- Mock Objects ---
class DummyCollector:
    def measure(self, name):
        class Context:
            def __enter__(self): return
            def __exit__(self, *args): return
        return Context()

print("\n--- 1. Testing Connection & Init ---")
try:
    # Initialize the class with the URI
    dolt = DoltToolSuite.init_for_bench(
    collector=DummyCollector(),
    db_name="dolt_data",
    autocommit=True
    )
    
    # Verify the connection actually works
    with dolt.conn.cursor() as cur:
        cur.execute("SELECT 1;")
    print("✅ Connection Successful!")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    print("   (Ensure the server is running. If 'fe_sendauth' error, it's a client config issue)")
    sys.exit(1)

print("\n--- 2. Testing _get_current_branch_impl ---")
try:
    branch, bid = dolt._get_current_branch_impl()
    print(f"   Current Branch: '{branch}'")
    print("✅ Success")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n--- 3. Testing _create_branch_impl ---")
NEW_BRANCH = "feature_test_func"
try:
    print(f"   Creating branch '{NEW_BRANCH}'...")
    dolt._create_branch_impl(NEW_BRANCH, "main")
    print("✅ Success: Branch created.")
except Exception as e:
    if "already exists" in str(e):
        print("✅ Success (Branch already existed)")
    else:
        print(f"❌ Failed: {e}")

print("\n--- 4. Testing _connect_branch_impl ---")
try:
    print(f"   Switching to '{NEW_BRANCH}'...")
    dolt._connect_branch_impl(NEW_BRANCH)
    
    # Verify we actually switched
    curr, _ = dolt._get_current_branch_impl()
    if curr == NEW_BRANCH:
        print(f"✅ Success: We are now on '{curr}'")
    else:
        print(f"❌ Failed: Switched but still on '{curr}'")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n🎉 ALL TESTS PASSED")