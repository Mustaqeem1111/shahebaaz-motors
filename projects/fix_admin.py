import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

print("Fixing admin username...")

conn = sqlite3.connect("shahebaz_motors.db")
cursor = conn.cursor()

# Password set karo
new_password = "Shahebaz@Motors2026!"
password_hash = generate_password_hash(new_password)
now = datetime.now().isoformat(timespec="seconds")

# Step 1: Check karo "admin" exist karta hai
cursor.execute("SELECT id FROM admin_users WHERE username = 'admin'")
old_admin = cursor.fetchone()

# Step 2: Check karo "adminn" exist karta hai
cursor.execute("SELECT id FROM admin_users WHERE username = 'adminn'")
new_admin = cursor.fetchone()

if old_admin and not new_admin:
    # "admin" ko "adminn" karo
    cursor.execute("""
        UPDATE admin_users 
        SET username = 'adminn', password_hash = ?, updated_at = ?
        WHERE username = 'admin'
    """, (password_hash, now))
    print("✅ Username 'admin' → 'adminn' kar diya")
    
elif new_admin:
    # "adminn" already hai — password update karo
    cursor.execute("""
        UPDATE admin_users 
        SET password_hash = ?, updated_at = ?
        WHERE username = 'adminn'
    """, (password_hash, now))
    print("✅ 'adminn' password update kar diya")

else:
    # Dono nahi hain — naya banao
    cursor.execute("""
        INSERT INTO admin_users (username, email, password_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, ("adminn", "mahalatbademustaqeem@gmail.com", password_hash, now, now))
    print("✅ Naya 'adminn' user banaya")

conn.commit()

# Verify
cursor.execute("SELECT username, email, updated_at FROM admin_users")
print("\n=== FINAL STATE ===")
for row in cursor.fetchall():
    print(f"Username: {row[0]}")
    print(f"Email: {row[1]}")
    print(f"Updated: {row[2]}")

conn.close()
print("\nDone!")