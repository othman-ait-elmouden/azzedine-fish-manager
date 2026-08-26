from database.connection import db
from utils.security import hash_password

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL, full_name TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'موظف',
 is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS products(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT DEFAULT '',
 purchase_price REAL NOT NULL DEFAULT 0 CHECK(purchase_price>=0),
 sale_price REAL NOT NULL DEFAULT 0 CHECK(sale_price>=0), quantity REAL NOT NULL DEFAULT 0,
 unit TEXT NOT NULL DEFAULT 'كيلوغرام', barcode TEXT UNIQUE, low_stock REAL DEFAULT 5,
 image_path TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS customers(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT DEFAULT '', address TEXT DEFAULT '',
 created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS suppliers(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT DEFAULT '', address TEXT DEFAULT '',
 created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS invoices(
 id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_no TEXT UNIQUE NOT NULL, customer_id INTEGER,
 subtotal REAL NOT NULL, discount REAL NOT NULL DEFAULT 0, tax REAL NOT NULL DEFAULT 0,
 total REAL NOT NULL, payment_method TEXT NOT NULL, user_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL,
 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS invoice_items(
 id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER NOT NULL, product_id INTEGER,
 product_name TEXT NOT NULL, quantity REAL NOT NULL CHECK(quantity>0), unit_price REAL NOT NULL,
 purchase_price REAL NOT NULL DEFAULT 0, total REAL NOT NULL,
 FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
 FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS expenses(
 id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, amount REAL NOT NULL CHECK(amount>=0),
 expense_date TEXT NOT NULL, notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS fish_types(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
 is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(created_at);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);
"""

DEFAULT_SETTINGS = {
 "shop_name":"Azzedine Fish", "phone":"", "address":"", "currency":"د.م",
 "logo":"", "theme":"dark", "printer":"", "tax_rate":"0"
}

def initialize_database():
    with db.transaction() as con:
        con.executescript(SCHEMA)
        if not con.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            con.execute("INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)",
                        ("admin", hash_password("admin123"), "مدير النظام", "مدير"))
        con.executemany("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", DEFAULT_SETTINGS.items())
        con.executemany("INSERT OR IGNORE INTO fish_types(name) VALUES(?)", [
            ("السردين",),("الصول",),("الميرلان",),("الكروفيت",),("الكلمار",),
            ("الدوراد",),("القرب",),("التونة",),("أبو سيف",),("الراية",)
        ])
