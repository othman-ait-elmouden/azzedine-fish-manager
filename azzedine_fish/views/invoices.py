import customtkinter as ctk
from tkinter import messagebox,filedialog
from database.connection import db
from services.invoice_service import InvoiceService
from utils.invoice_pdf import generate_invoice_pdf,print_file
from views.widgets import button,DataTable

class InvoicesPage(ctk.CTkFrame):
    def __init__(self,parent,user):
        super().__init__(parent,fg_color="transparent"); self.user=user; self.cart=[]; self.customers=[]; self.next_id=1
        ctk.CTkLabel(self,text="إنشاء فاتورة",font=("Tahoma",24,"bold")).pack(anchor="e",pady=(0,10))
        form=ctk.CTkFrame(self); form.pack(fill="x",pady=5)
        self.customer=ctk.CTkComboBox(form,values=["زبون نقدي"],justify="right",width=240); self.customer.pack(side="right",padx=8,pady=12)
        self.product=ctk.CTkComboBox(form,values=["اكتب أو اختر اسم السمك"],justify="right",width=200); self.product.pack(side="right",padx=5)
        self.qty=ctk.CTkEntry(form,placeholder_text="الكمية",width=80,justify="right"); self.qty.pack(side="right",padx=5)
        self.unit=ctk.CTkOptionMenu(form,values=["كيلوغرام","قطعة"],width=100); self.unit.pack(side="right",padx=5)
        self.purchase=ctk.CTkEntry(form,placeholder_text="سعر الشراء",width=100,justify="right"); self.purchase.pack(side="right",padx=5)
        self.price=ctk.CTkEntry(form,placeholder_text="سعر البيع",width=100,justify="right"); self.price.pack(side="right",padx=5)
        button(form,"إضافة للسلة",self.add_item,width=120).pack(side="right",padx=8)
        self.table=DataTable(self,["id","name","qty","unit","purchase","price","total"],["#","البضاعة","الكمية","الوحدة","الشراء","البيع","المجموع"]); self.table.pack(fill="both",expand=True,pady=8)
        totals=ctk.CTkFrame(self); totals.pack(fill="x")
        self.discount=ctk.CTkEntry(totals,placeholder_text="الخصم",width=120,justify="right"); self.discount.pack(side="right",padx=6,pady=10); self.discount.insert(0,"0")
        self.tax=ctk.CTkEntry(totals,placeholder_text="الضريبة",width=120,justify="right"); self.tax.pack(side="right",padx=6); self.tax.insert(0,"0")
        self.payment=ctk.CTkOptionMenu(totals,values=["نقداً","بطاقة","تحويل"]); self.payment.pack(side="right",padx=6)
        self.paper=ctk.CTkOptionMenu(totals,values=["A4","80mm","58mm"],width=90); self.paper.pack(side="right",padx=6)
        button(totals,"حذف المنتج",self.remove_item,fg_color="#D9534F",width=110).pack(side="left",padx=5)
        self.total_label=ctk.CTkLabel(totals,text="المجموع: 0.00 د.م",font=("Tahoma",18,"bold")); self.total_label.pack(side="left",padx=15)
        button(self,"حفظ الفاتورة وطباعة PDF",self.save).pack(anchor="w",pady=10); self.load()
    def load(self):
        self.customers=db.query("SELECT * FROM customers ORDER BY name")
        fish=db.query("SELECT name FROM fish_types WHERE is_active=1 ORDER BY name")
        self.customer.configure(values=["زبون نقدي"]+[f"{r['id']} - {r['name']}" for r in self.customers])
        self.product.configure(values=[r["name"] for r in fish] or ["اكتب اسم السمك"])
        self.product.set("")
    def add_item(self):
        try:
            name=self.product.get().strip(); qty=float(self.qty.get()); purchase=float(self.purchase.get() or 0); price=float(self.price.get())
            if not name or qty<=0 or purchase<0 or price<0: raise ValueError
        except Exception: return messagebox.showerror("خطأ","أدخل اسم البضاعة والكمية والأسعار بشكل صحيح")
        self.cart.append({"line_id":self.next_id,"name":name,"quantity":qty,"unit":self.unit.get(),"purchase_price":purchase,"price":price}); self.next_id+=1
        self.product.set("")
        for entry in (self.qty,self.purchase,self.price): entry.delete(0,"end")
        self.product.focus(); self.refresh()
    def refresh(self):
        self.table.fill([[x["line_id"],x["name"],x["quantity"],x["unit"],f"{x['purchase_price']:.2f}",f"{x['price']:.2f}",f"{x['quantity']*x['price']:.2f}"] for x in self.cart])
        total=sum(x["quantity"]*x["price"] for x in self.cart)-float(self.discount.get() or 0)+float(self.tax.get() or 0)
        self.total_label.configure(text=f"المجموع: {max(total,0):.2f} د.م")
    def remove_item(self):
        line_id=self.table.selected_id(); self.cart=[x for x in self.cart if str(x["line_id"])!=str(line_id)]; self.refresh()
    def save(self):
        try:
            cid=None if self.customer.get()=="زبون نقدي" else int(self.customer.get().split(" - ")[0])
            iid,no,total=InvoiceService.create(cid,self.cart,self.discount.get(),self.tax.get(),self.payment.get(),self.user["id"])
            invoice,items=InvoiceService.details(iid); path=generate_invoice_pdf(invoice,items,self.paper.get())
            messagebox.showinfo("تم",f"تم حفظ الفاتورة {no}\n{path}"); self.cart=[]; self.refresh(); self.load()
        except Exception as e: messagebox.showerror("خطأ",str(e))

class InvoiceHistoryPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent"); ctk.CTkLabel(self,text="سجل الفواتير",font=("Tahoma",24,"bold")).pack(anchor="e")
        self.table=DataTable(self,["id","no","customer","total","payment","date"],["#","رقم الفاتورة","الزبون","المجموع","الدفع","التاريخ"]); self.table.pack(fill="both",expand=True,pady=10)
        bar=ctk.CTkFrame(self,fg_color="transparent"); bar.pack(fill="x"); button(bar,"فتح PDF",self.pdf).pack(side="right",padx=5); button(bar,"طباعة",lambda:self.pdf(True)).pack(side="right",padx=5); self.refresh()
    def refresh(self):
        rows=db.query("SELECT i.*,COALESCE(c.name,'زبون نقدي') customer FROM invoices i LEFT JOIN customers c ON c.id=i.customer_id ORDER BY i.id DESC"); self.table.fill([[r["id"],r["invoice_no"],r["customer"],f"{r['total']:.2f}",r["payment_method"],r["created_at"]] for r in rows])
    def pdf(self,printing=False):
        iid=self.table.selected_id()
        if not iid:return messagebox.showwarning("تنبيه","اختر فاتورة")
        inv,items=InvoiceService.details(iid); path=generate_invoice_pdf(inv,items)
        if printing: print_file(path)
        else:
            import os; os.startfile(path) if os.name=="nt" else os.system(f"xdg-open '{path}'")
