from datetime import datetime
from database.connection import db

class InvoiceService:
    @staticmethod
    def create(customer_id, items, discount, tax, payment, user_id):
        if not items: raise ValueError("أضف منتجاً واحداً على الأقل")
        with db.transaction() as con:
            checked=[]
            for item in items:
                qty=float(item["quantity"])
                name=str(item.get("name","")).strip()
                sale_price=float(item.get("price",0))
                purchase_price=float(item.get("purchase_price",0))
                unit=str(item.get("unit","كيلوغرام"))
                if not name or qty<=0 or sale_price<0 or purchase_price<0:
                    raise ValueError("بيانات البضاعة غير صالحة")
                checked.append((name,qty,sale_price,purchase_price,unit))
            subtotal=sum(sale*q for _,q,sale,_,_ in checked)
            discount=max(0,float(discount or 0)); tax=max(0,float(tax or 0))
            total=max(0, subtotal-discount+tax)
            no=datetime.now().strftime("AF-%Y%m%d-%H%M%S-%f")[:25]
            cur=con.execute("INSERT INTO invoices(invoice_no,customer_id,subtotal,discount,tax,total,payment_method,user_id) VALUES(?,?,?,?,?,?,?,?)",
                (no,customer_id,subtotal,discount,tax,total,payment,user_id))
            invoice_id=cur.lastrowid
            for name,q,sale,purchase,unit in checked:
                con.execute("INSERT INTO invoice_items(invoice_id,product_id,product_name,quantity,unit_price,purchase_price,total) VALUES(?,?,?,?,?,?,?)",
                    (invoice_id,None,name,q,sale,purchase,q*sale))
            return invoice_id,no,total
    @staticmethod
    def details(invoice_id):
        head=db.one("SELECT i.*,c.name customer_name FROM invoices i LEFT JOIN customers c ON c.id=i.customer_id WHERE i.id=?",(invoice_id,))
        return head,db.query("SELECT * FROM invoice_items WHERE invoice_id=?",(invoice_id,))
