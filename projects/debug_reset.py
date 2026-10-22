import sqlite3
from werkzeug.security import check_password_hash

print("=" * 50)
print("SHAHEBAZ MOTORS - RESET PASSWORD DEBUG")
print("=" * 50)

# =========================================================
# STEP 1: Database Check
# =========================================================

print("\n[STEP 1] Database mein admin users:")
print("-" * 50)

conn = sqlite3.connect("shahebaz_motors.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, username, email, updated_at, 
           LENGTH(password_hash) as hash_len 
    FROM admin_users
""")

rows = cursor.fetchall()
print(f"Total users: {len(rows)}")

for row in rows:
    print("---")
    print(f"ID:          {row['id']}")
    print(f"Username:    {row['username']}")
    print(f"Email:       {row['email']}")
    print(f"Updated:     {row['updated_at']}")
    print(f"Hash length: {row['hash_len']}")

conn.close()


# =========================================================
# STEP 2: Password Test
# =========================================================

print("\n[STEP 2] Password Test:")
print("-" * 50)

# YAHAN APNA NAYA PASSWORD DAALO
test_passwords = [
    "Shahebaz@Motors2026!",       # .env wala
    # "YOUR_NEW_PASSWORD",        # Naya password (uncomment karke daalo)
]

conn = sqlite3.connect("shahebaz_motors.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT username, password_hash FROM admin_users WHERE username = 'adminn'")
row = cursor.fetchone()

if row:
    print(f"User found: {row['username']}")
    print(f"Hash (first 40): {row['password_hash'][:40]}...")
    
    for test_pwd in test_passwords:
        result = check_password_hash(row["password_hash"], test_pwd)
        status = "✅ MATCH" if result else "❌ NO MATCH"
        print(f"Password '{test_pwd[:10]}...' → {status}")
else:
    print("❌ User 'adminn' NOT FOUND in database!")

conn.close()


# =========================================================
# STEP 3: Summary
# =========================================================

print("\n" + "=" * 50)
print("DEBUG COMPLETE")
print("=" * 50)