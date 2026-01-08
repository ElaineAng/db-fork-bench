import inspect
import sys
from dblib.dolt import DoltToolSuite

print("--- 1. INSPECTING CLASS SIGNATURE ---")
try:
    # This prints exactly what the __init__ function expects
    sig = inspect.signature(DoltToolSuite.__init__)
    print(f"REQUIRED ARGUMENTS: {sig}")
except Exception as e:
    print(f"Could not inspect signature: {e}")

# --- 2. CONFIGURATION ---
# We try to satisfy the requirements we saw in your error logs
URI = "postgresql://root:password@127.0.0.1:5432/dolt_data"

class DummyCollector:
    def measure(self, name):
        class Context:
            def __enter__(self): return
            def __exit__(self, *args): return
        return Context()

print("\n--- 3. ATTEMPTING INSTANTIATION (Keyword Args) ---")
try:
    # We use 'Keyword Arguments' (name=value) to force the match.
    # If the names are wrong, Python will tell us the correct names.
    dolt = DoltToolSuite(
        collector=DummyCollector(), 
        connection_uri=URI, 
        autocommit=True
    )
    print("✅ INSTANTIATION SUCCESSFUL!")
    
    # Test Connection
    with dolt.conn.cursor() as cur:
        cur.execute("SELECT 1;")
    print("✅ DB CONNECTION SUCCESSFUL!")
    
    # Run the Function Test
    print("\n--- 4. TESTING FUNCTIONS ---")
    branch_name = "test_branch_debug"
    
    # Create
    print(f"Creating branch '{branch_name}'...")
    dolt._create_branch_impl(branch_name, "main")
    print("✅ Created.")
    
    # Switch
    print(f"Switching to '{branch_name}'...")
    dolt._connect_branch_impl(branch_name)
    print("✅ Switched.")
    
    # Check
    curr, _ = dolt._get_current_branch_impl()
    print(f"Current Branch: {curr}")
    if curr == branch_name:
        print("🎉 SUCCESS: EVERYTHING WORKS!")
    else:
        print(f"❌ FAIL: Expected {branch_name}, got {curr}")

except TypeError as te:
    print(f"❌ SIGNATURE ERROR: {te}")
    print("   (This means the argument names above are wrong. Check the 'REQUIRED ARGUMENTS' line)")
except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
    