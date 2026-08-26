import customtkinter as ctk
from tkinter import messagebox,filedialog
from datetime import date
from views.widgets import button,DataTable
from models.repositories import ProductRepository,CustomerRepository,SupplierRepository,ExpenseRepository
from config import CARD_DARK,DANGER

class FormDialog(ctk.CTkToplevel):
    def __init__(self,parent,title,fields,initial=None):
        super().__init__(parent); self.title(title); self.geometry("480x620"); self.resizable(False,False); self.result=None; self.grab_set(); self.fields={}; initial=initial or {}
        ctk.CTkLabel(self,text=title,font=("Tahoma",22,"bold")).pack(pady=18)
        body=ctk.CTkScrollableFrame(self,fg_color="transparent"); body.pack(fill="both",expand=True,padx=25)
        for key,label,kind,default in fields:
            ctk.CTkLabel(body,text=label,font=("Tahoma",12),anchor="e").pack(fill="x",pady=(8,2))
            value=str(initial.get(key,default) or "")
            if kind=="choice":
                e=ctk.CTkOptionMenu(body,values=default); e.set(value if value in default else default[0])
            else:
                e=ctk.CTkEntry(body,justify="right"); e.insert(0,value)
            e.pack(fill="x"); self.fields[key]=e
        button(self,"حفظ",self.save).pack(fill="x",padx=25,pady=18)
    def save(self): self.result={k:w.get().strip() for k,w in self.fields.items()}; self.destroy()

class CrudPage(ctk.CTkFrame):
    title=""; repo=None; fields=[]; columns=[]; headings=[]
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent"); self.repo=self.repo()
        top=ctk.CTkFrame(self,fg_color="transparent"); top.pack(fill="x",pady=(0,12))
        ctk.CTkLabel(top,text=self.title,font=("Tahoma",24,"bold")).pack(side="right")
        button(top,"إضافة +",self.add,width=100).pack(side="left",padx=4)
        button(top,"تعديل",self.edit,width=90).pack(side="left",padx=4)
        button(top,"حذف",self.delete,width=90,fg_color=DANGER).pack(side="left",padx=4)
        self.search=ctk.CTkEntry(top,placeholder_text="بحث فوري...",justify="right",width=220); self.search.pack(side="left",padx=10); self.search.bind("<KeyRelease>",lambda e:self.refresh())
        self.table=DataTable(self,self.columns,self.headings); self.table.pack(fill="both",expand=True); self.refresh()
    def values(self,r): return [r[c] for c in self.columns]
    def refresh(self): self.table.fill([self.values(r) for r in self.repo.all(self.search.get())])
    def clean(self,data): return data
    def add(self):
        d=FormDialog(self,self.title,self.fields); self.wait_window(d)
        if d.result:
            try: self.repo.create(self.clean(d.result)); self.refresh()
            except Exception as e: messagebox.showerror("خطأ",str(e))
    def edit(self):
        row_id=self.table.selected_id()
        if not row_id: return messagebox.showwarning("تنبيه","اختر صفاً أولاً")
        row=dict(self.repo.get(row_id)); d=FormDialog(self,"تعديل",self.fields,row); self.wait_window(d)
        if d.result:
            try: self.repo.update(row_id,self.clean(d.result)); self.refresh()
            except Exception as e: messagebox.showerror("خطأ",str(e))
    def delete(self):
        row_id=self.table.selected_id()
        if row_id and messagebox.askyesno("تأكيد","هل تريد الحذف؟"):
            try: self.repo.delete(row_id); self.refresh()
            except Exception as e: messagebox.showerror("تعذر الحذف",str(e))

class ProductsPage(CrudPage):
    title="إدارة المنتجات"; repo=ProductRepository
    columns=["id","name","category","purchase_price","sale_price","quantity","unit","barcode","low_stock"]
    headings=["#","الاسم","الصنف","الشراء","البيع","الكمية","الوحدة","الباركود","حد التنبيه"]
    fields=[("name","اسم المنتج","text",""),("category","الصنف","text",""),("purchase_price","سعر الشراء","number","0"),("sale_price","سعر البيع","number","0"),("quantity","الكمية","number","0"),("unit","الوحدة","choice",["كيلوغرام","قطعة"]),("barcode","الباركود","text",""),("low_stock","تنبيه انخفاض المخزون","number","5"),("image_path","مسار الصورة","text","")]
    def clean(self,d):
        for k in ("purchase_price","sale_price","quantity","low_stock"): d[k]=float(d[k] or 0)
        d["barcode"]=d["barcode"] or None; return d

class CustomersPage(CrudPage):
    title="إدارة الزبائن"; repo=CustomerRepository; columns=["id","name","phone","address","purchases","invoices"]
    headings=["#","الاسم","الهاتف","العنوان","إجمالي المشتريات","عدد الفواتير"]
    fields=[("name","اسم الزبون","text",""),("phone","رقم الهاتف","text",""),("address","العنوان","text","")]
    def __init__(self,parent):
        ctk.CTkFrame.__init__(self,parent,fg_color="transparent"); self.repo=self.repo()
        top=ctk.CTkFrame(self,fg_color="transparent"); top.pack(fill="x",pady=(0,8))
        ctk.CTkLabel(top,text=self.title,font=("Tahoma",24,"bold")).pack(side="right")
        button(top,"إضافة +",self.add,width=90).pack(side="left",padx=3)
        button(top,"تعديل",self.edit,width=80).pack(side="left",padx=3)
        button(top,"حذف",self.delete,width=80,fg_color=DANGER).pack(side="left",padx=3)
        self.search=ctk.CTkEntry(top,placeholder_text="بحث عن زبون...",justify="right",width=210); self.search.pack(side="left",padx=8); self.search.bind("<KeyRelease>",lambda e:self.refresh())
        self.table=DataTable(self,self.columns,self.headings); self.table.pack(fill="both",expand=True,pady=(0,8))
        self.table.tree.bind("<<TreeviewSelect>>",self.load_customer_invoices)
        invoice_header=ctk.CTkFrame(self,fg_color="transparent"); invoice_header.pack(fill="x",pady=(3,5))
        self.customer_summary=ctk.CTkLabel(invoice_header,text="اختر زبوناً لعرض جميع فواتيره",font=("Tahoma",16,"bold")); self.customer_summary.pack(side="right")
        button(invoice_header,"فتح الفاتورة",lambda:self.open_invoice(False),width=110).pack(side="left",padx=3)
        button(invoice_header,"طباعة",lambda:self.open_invoice(True),width=85).pack(side="left",padx=3)
        self.invoice_table=DataTable(self,["id","no","total","payment","date"],["#","رقم الفاتورة","المجموع","طريقة الدفع","التاريخ"])
        self.invoice_table.configure(height=210); self.invoice_table.pack(fill="both",expand=True); self.refresh()
    def refresh(self):
        from database.connection import db
        rows=db.query("SELECT c.*,COALESCE(SUM(i.total),0) purchases,COUNT(i.id) invoices FROM customers c LEFT JOIN invoices i ON i.customer_id=c.id WHERE c.name LIKE ? GROUP BY c.id ORDER BY c.id DESC",(f"%{self.search.get()}%",)); self.table.fill([self.values(r) for r in rows])
        if hasattr(self,"invoice_table"): self.invoice_table.fill([]); self.customer_summary.configure(text="اختر زبوناً لعرض جميع فواتيره")
    def load_customer_invoices(self,_=None):
        from database.connection import db
        customer_id=self.table.selected_id()
        if not customer_id: return
        customer=db.one("SELECT name FROM customers WHERE id=?",(customer_id,))
        rows=db.query("SELECT id,invoice_no,total,payment_method,created_at FROM invoices WHERE customer_id=? ORDER BY id DESC",(customer_id,))
        self.invoice_table.fill([[r["id"],r["invoice_no"],f"{r['total']:.2f} د.م",r["payment_method"],r["created_at"]] for r in rows])
        total=sum(r["total"] for r in rows)
        self.customer_summary.configure(text=f"فواتير {customer['name']}: {len(rows)} — الإجمالي: {total:.2f} د.م")
    def open_invoice(self,printing=False):
        invoice_id=self.invoice_table.selected_id()
        if not invoice_id: return messagebox.showwarning("تنبيه","اختر فاتورة من قائمة فواتير الزبون")
        from services.invoice_service import InvoiceService
        from utils.invoice_pdf import generate_invoice_pdf,print_file
        invoice,items=InvoiceService.details(invoice_id); path=generate_invoice_pdf(invoice,items)
        if printing: print_file(path)
        else:
            import os
            os.startfile(path) if os.name=="nt" else os.system(f"xdg-open '{path}'")

class SuppliersPage(CrudPage):
    title="إدارة الموردين"; repo=SupplierRepository; columns=["id","name","phone","address"]; headings=["#","الاسم","الهاتف","العنوان"]
    fields=[("name","اسم المورد","text",""),("phone","الهاتف","text",""),("address","العنوان","text","")]

class ExpensesPage(CrudPage):
    title="المصاريف"; repo=ExpenseRepository; columns=["id","category","amount","expense_date","notes"]; headings=["#","التصنيف","القيمة","التاريخ","ملاحظات"]
    fields=[("category","تصنيف المصروف","text",""),("amount","القيمة","number","0"),("expense_date","التاريخ YYYY-MM-DD","text",str(date.today())),("notes","ملاحظات","text","")]
    def clean(self,d): d["amount"]=float(d["amount"] or 0); return d
