import sqlite3
conn = sqlite3.connect(r'C:\Users\DELL\OneDrive\Desktop\Factly\backend\db.sqlite3')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM auth_user")
print("Users count:", cursor.fetchone()[0])
cursor.execute("SELECT id, username, email FROM auth_user LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print("User:", row)
conn.close()
