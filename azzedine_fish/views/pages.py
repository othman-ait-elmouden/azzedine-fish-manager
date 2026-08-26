import customtkinter as ctk
from tkinter import messagebox,filedialog
from pathlib import Path
from database.connection import db
from services.report_service import ReportService
from services.auth_service import AuthService
from utils.backup import create_backup,restore_backup
from utils.exporter import export_csv,export_excel
from config import EXPORT_DIR
from views.widgets import StatCard,button,DataTable
from views.crud import FormDialog

class DashboardPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent"); data=ReportService.dashboard(); profit=ReportService.net_profit()
        ctk.CTkLabel(self,text="لوحة التحكم",font=("Tahoma",25,"bold")).pack(anchor="e",pady=(0,12))
        cards=ctk.CTkFrame(self,fg_color="transparent"); cards.pack(fill="x")
        items=[("عدد الزبائن",data["customers"],"👥"),("عدد الفواتير",data["invoices"],"🧾"),("مبيعات اليوم",f"{data['daily_sales']:.2f} د.م","💰"),("مبيعات الشهر",f"{data['monthly_sales']:.2f} د.م","📈"),("الربح الصافي",f"{profit:.2f} د.م","✅")]
        for i,x in enumerate(items):
            card=StatCard(cards,*x); card.grid(row=i//4,column=i%4,padx=6,pady=6,sticky="nsew"); cards.grid_columnconfigure(i%4,weight=1)
        ctk.CTkLabel(self,text="آخر الفواتير",font=("Tahoma",18,"bold")).pack(anchor="e",pady=(18,5))
        t=DataTable(self,["no","customer","total","date"],["الفاتورة","الزبون","المجموع","التاريخ"]); t.pack(fill="both",expand=True)
        rows=db.query("SELECT i.invoice_no,COALESCE(c.name,'نقدي') customer,i.total,i.created_at FROM invoices i LEFT JOIN customers c ON c.id=i.customer_id ORDER BY i.id DESC LIMIT 10"); t.fill([[r["invoice_no"],r["customer"],f"{r['total']:.2f}",r["created_at"]] for r in rows])

class ReportsPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent"); ctk.CTkLabel(self,text="التقارير والأرباح",font=("Tahoma",24,"bold")).pack(anchor="e")
        bar=ctk.CTkFrame(self,fg_color="transparent"); bar.pack(fill="x",pady=10)
        self.period=ctk.CTkOptionMenu(bar,values=["اليوم","الأسبوع","الشهر","السنة"],command=lambda _:self.refresh()); self.period.pack(side="right",padx=5)
        button(bar,"Excel",lambda:self.export("xlsx"),width=80).pack(side="left",padx=3); button(bar,"CSV",lambda:self.export("csv"),width=80).pack(side="left",padx=3)
        self.table=DataTable(self,["day","count","sales","profit"],["التاريخ","الفواتير","المبيعات","الربح الإجمالي"]); self.table.pack(fill="both",expand=True); self.refresh()
    def rows(self):
        mods={"اليوم":"0 days","الأسبوع":"-6 days","الشهر":"start of month","السنة":"start of year"}; return ReportService.period(mods[self.period.get()])
    def refresh(self): self.table.fill([[r["day"],r["invoices"],round(r["sales"],2),round(r["gross_profit"] or 0,2)] for r in self.rows()])
    def export(self,typ):
        rows=[[r["day"],r["invoices"],r["sales"],r["gross_profit"]] for r in self.rows()]; headers=["التاريخ","الفواتير","المبيعات","الربح"]
        path=EXPORT_DIR/f"report.{typ}"; export_excel(path,headers,rows) if typ=="xlsx" else export_csv(path,headers,rows); messagebox.showinfo("تم",str(path))

class SettingsPage(ctk.CTkFrame):
    def __init__(self,parent,app):
        super().__init__(parent,fg_color="transparent"); self.app=app; self.inputs={}; current={r["key"]:r["value"] for r in db.query("SELECT * FROM settings")}
        ctk.CTkLabel(self,text="الإعدادات",font=("Tahoma",24,"bold")).pack(anchor="e")
        form=ctk.CTkScrollableFrame(self); form.pack(fill="both",expand=True,pady=10)
        for key,label in (("shop_name","اسم المحل"),("phone","الهاتف"),("address","العنوان"),("currency","العملة"),("logo","مسار الشعار"),("printer","اسم الطابعة"),("tax_rate","نسبة الضريبة")):
            ctk.CTkLabel(form,text=label,anchor="e").pack(fill="x",padx=25,pady=(8,2)); e=ctk.CTkEntry(form,justify="right"); e.insert(0,current.get(key,"")); e.pack(fill="x",padx=25); self.inputs[key]=e
        button(form,"اختيار صورة الشعار",self.choose_logo,width=180).pack(anchor="e",padx=25,pady=(6,2))
        self.theme=ctk.CTkOptionMenu(form,values=["dark","light"]); self.theme.set(current.get("theme","dark")); self.theme.pack(pady=12)
        button(form,"حفظ الإعدادات",self.save).pack(pady=8); button(form,"إنشاء نسخة احتياطية",self.backup).pack(pady=8); button(form,"استعادة نسخة احتياطية",self.restore).pack(pady=8)
        ctk.CTkLabel(form,text="قائمة أنواع الأسماك",font=("Tahoma",19,"bold")).pack(anchor="e",fill="x",padx=25,pady=(25,8))
        fish_bar=ctk.CTkFrame(form,fg_color="transparent"); fish_bar.pack(fill="x",padx=25)
        self.fish_name=ctk.CTkEntry(fish_bar,placeholder_text="اكتب اسم السمك",justify="right"); self.fish_name.pack(side="right",fill="x",expand=True,padx=(5,0))
        button(fish_bar,"إضافة",self.add_fish,width=80).pack(side="right",padx=4)
        button(fish_bar,"تعديل",self.edit_fish,width=80).pack(side="right",padx=4)
        button(fish_bar,"حذف",self.delete_fish,width=80,fg_color="#D9534F").pack(side="right",padx=4)
        self.fish_table=DataTable(form,["id","name"],["#","اسم السمك"]); self.fish_table.configure(height=230); self.fish_table.pack(fill="x",padx=25,pady=10)
        self.fish_table.tree.bind("<<TreeviewSelect>>",self.select_fish); self.refresh_fish()
    def save(self):
        with db.transaction() as con:
            for k,e in self.inputs.items(): con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(k,e.get()))
            con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('theme',?)",(self.theme.get(),))
        ctk.set_appearance_mode(self.theme.get()); messagebox.showinfo("تم","حُفظت الإعدادات")
    def choose_logo(self):
        path=filedialog.askopenfilename(title="اختيار شعار Azzedine Fish",filetypes=[("صور الشعار","*.png *.jpg *.jpeg *.webp"),("كل الملفات","*.*")])
        if path:
            self.inputs["logo"].delete(0,"end"); self.inputs["logo"].insert(0,path)
    def backup(self): messagebox.showinfo("تم",f"تم إنشاء النسخة:\n{create_backup()}")
    def restore(self):
        p=filedialog.askopenfilename(filetypes=[("SQLite","*.db")])
        if p and messagebox.askyesno("تأكيد","سيتم استبدال البيانات الحالية. هل تتابع؟"):
            try: restore_backup(p); messagebox.showinfo("تم","تمت الاستعادة. أعد تشغيل البرنامج.")
            except Exception as e: messagebox.showerror("خطأ",str(e))
    def refresh_fish(self):
        rows=db.query("SELECT id,name FROM fish_types WHERE is_active=1 ORDER BY name")
        self.fish_table.fill([[r["id"],r["name"]] for r in rows])
    def select_fish(self,_=None):
        selected=self.fish_table.tree.selection()
        if selected:
            values=self.fish_table.tree.item(selected[0],"values"); self.fish_name.delete(0,"end"); self.fish_name.insert(0,values[1])
    def add_fish(self):
        name=self.fish_name.get().strip()
        if not name: return messagebox.showwarning("تنبيه","اكتب اسم السمك")
        try:
            db.execute("INSERT INTO fish_types(name) VALUES(?)",(name,)); self.fish_name.delete(0,"end"); self.refresh_fish()
        except Exception: messagebox.showerror("خطأ","هذا الاسم موجود مسبقاً")
    def edit_fish(self):
        row_id=self.fish_table.selected_id(); name=self.fish_name.get().strip()
        if not row_id or not name: return messagebox.showwarning("تنبيه","اختر اسماً ثم اكتب الاسم الجديد")
        try: db.execute("UPDATE fish_types SET name=? WHERE id=?",(name,row_id)); self.refresh_fish()
        except Exception: messagebox.showerror("خطأ","هذا الاسم موجود مسبقاً")
    def delete_fish(self):
        row_id=self.fish_table.selected_id()
        if row_id and messagebox.askyesno("تأكيد","حذف اسم السمك من قائمة الاختيار؟"):
            db.execute("DELETE FROM fish_types WHERE id=?",(row_id,)); self.fish_name.delete(0,"end"); self.refresh_fish()

class UsersPage(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent,fg_color="transparent"); ctk.CTkLabel(self,text="إدارة المستخدمين والصلاحيات",font=("Tahoma",24,"bold")).pack(anchor="e")
        button(self,"إضافة مستخدم",self.add).pack(anchor="e",pady=8); self.table=DataTable(self,["id","username","name","role","active"],["#","المستخدم","الاسم","الصلاحية","نشط"]); self.table.pack(fill="both",expand=True); self.refresh()
    def refresh(self): self.table.fill([[r["id"],r["username"],r["full_name"],r["role"],"نعم" if r["is_active"] else "لا"] for r in AuthService.users()])
    def add(self):
        d=FormDialog(self,"إضافة مستخدم",[("username","اسم المستخدم","text",""),("password","كلمة المرور","text",""),("full_name","الاسم الكامل","text",""),("role","الصلاحية","choice",["مدير","موظف"])]); self.wait_window(d)
        if d.result:
            try: AuthService.add_user(**d.result); self.refresh()
            except Exception as e: messagebox.showerror("خطأ",str(e))
