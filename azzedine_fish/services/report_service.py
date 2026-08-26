from database.connection import db

class ReportService:
    @staticmethod
    def dashboard():
        return dict(db.one("""SELECT
        (SELECT COUNT(*) FROM products) products,(SELECT COUNT(*) FROM customers) customers,
        (SELECT COUNT(*) FROM invoices) invoices,
        COALESCE((SELECT SUM(total) FROM invoices WHERE date(created_at)=date('now','localtime')),0) daily_sales,
        COALESCE((SELECT SUM(total) FROM invoices WHERE strftime('%Y-%m',created_at)=strftime('%Y-%m','now','localtime')),0) monthly_sales,
        COALESCE((SELECT SUM(quantity*sale_price) FROM products),0) stock_value"""))
    @staticmethod
    def period(modifier="start of month"):
        return db.query("""WITH item_profit AS (
        SELECT invoice_id,SUM((unit_price-purchase_price)*quantity) profit FROM invoice_items GROUP BY invoice_id)
        SELECT date(i.created_at) day,COUNT(i.id) invoices,SUM(i.total) sales,
        SUM(COALESCE(p.profit,0)-i.discount) gross_profit
        FROM invoices i LEFT JOIN item_profit p ON p.invoice_id=i.id
        WHERE date(i.created_at)>=date('now',?) GROUP BY date(i.created_at) ORDER BY day""",(modifier,))
    @staticmethod
    def net_profit():
        r=db.one("""SELECT COALESCE((SELECT SUM((unit_price-purchase_price)*quantity) FROM invoice_items),0)-
        COALESCE((SELECT SUM(discount) FROM invoices),0)-COALESCE((SELECT SUM(amount) FROM expenses),0) value""")
        return r["value"]
    @staticmethod
    def best_products(): return db.query("SELECT product_name,SUM(quantity) quantity,SUM(total) total FROM invoice_items GROUP BY product_name ORDER BY quantity DESC LIMIT 10")
    @staticmethod
    def low_stock(): return db.query("SELECT * FROM products WHERE quantity<=low_stock ORDER BY quantity")
