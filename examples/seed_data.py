import random, sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def seed_database(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    now = datetime(2026, 7, 30)

    c.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, age INTEGER, tier TEXT, region TEXT, total_spent REAL, signup_date TEXT, created_at TEXT)")
    for i in range(1, 501):
        age = max(18, min(90, int(random.gauss(38, 12))))
        c.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)", (i, f"Customer_{i}", f"user{i}@example.com", age, random.choice(["standard","premium","enterprise","vip"]), random.choice(["US","EU","APAC"]), round(random.uniform(0,50000),2), (now - timedelta(days=random.randint(1,730))).date().isoformat(), (now - timedelta(days=random.randint(1,730))).isoformat()))

    for idx in [47, 193, 401]:
        c.execute("UPDATE customers SET age = ? WHERE id = ?", (random.choice([-5, 150, 999]), idx))

    c.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, status TEXT, category TEXT, created_at TEXT, updated_at TEXT)")
    for i in range(1, 2001):
        c.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?)", (i, random.randint(1,500), round(random.uniform(5,2000),2), random.choice(["completed","pending","shipped"]), random.choice(["general","electronics"]), (now - timedelta(hours=random.randint(1,720))).isoformat(), (now - timedelta(hours=random.randint(1,720))).isoformat()))

    for idx in [15, 289, 567, 1234, 1888]:
        c.execute("UPDATE orders SET amount = round(random.uniform(50000, 250000), 2) WHERE id = ?", (idx,))

    c.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER, created_at TEXT)")
    for i in range(1, 21):
        c.execute("INSERT INTO products VALUES (?,?,?,?,?,?)", (i, f"Product_{i}", random.choice(["Electronics","Clothing","Home"]), round(random.uniform(5,300),2), random.randint(0,500), (now - timedelta(days=random.randint(1,365))).isoformat()))

    c.execute("UPDATE products SET price = 9999.99 WHERE id = 3")
    conn.commit()
    conn.close()
    print(f"Seeded: {db_path}")

if __name__ == "__main__":
    seed_database("data/anomaly.db")