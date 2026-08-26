from database.connection import db

class Repository:
    table = ""
    allowed = set()
    def all(self, search=""):
        if search and "name" in self.allowed:
            return db.query(f"SELECT * FROM {self.table} WHERE name LIKE ? ORDER BY id DESC", (f"%{search}%",))
        return db.query(f"SELECT * FROM {self.table} ORDER BY id DESC")
    def get(self, row_id): return db.one(f"SELECT * FROM {self.table} WHERE id=?", (row_id,))
    def create(self, data):
        data = {k:v for k,v in data.items() if k in self.allowed}
        cols = ",".join(data); marks = ",".join("?" for _ in data)
        return db.execute(f"INSERT INTO {self.table}({cols}) VALUES({marks})", tuple(data.values()))
    def update(self, row_id, data):
        data = {k:v for k,v in data.items() if k in self.allowed}
        sets = ",".join(f"{k}=?" for k in data)
        db.execute(f"UPDATE {self.table} SET {sets} WHERE id=?", (*data.values(), row_id))
    def delete(self, row_id): db.execute(f"DELETE FROM {self.table} WHERE id=?", (row_id,))

class ProductRepository(Repository):
    table="products"; allowed={"name","category","purchase_price","sale_price","quantity","unit","barcode","low_stock","image_path"}
class CustomerRepository(Repository):
    table="customers"; allowed={"name","phone","address"}
class SupplierRepository(Repository):
    table="suppliers"; allowed={"name","phone","address"}
class ExpenseRepository(Repository):
    table="expenses"; allowed={"category","amount","expense_date","notes"}

