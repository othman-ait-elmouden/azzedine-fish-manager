import customtkinter as ctk
from config import APP_NAME,BG_DARK,PRIMARY,ACCENT
from database.schema import initialize_database
from views.login import LoginView
from views.crud import CustomersPage,SuppliersPage,ExpensesPage
from views.invoices import InvoicesPage,InvoiceHistoryPage
from views.pages import DashboardPage,ReportsPage,SettingsPage,UsersPage

class AzzedineFishApp(ctk.CTk):
    def __init__(self):
        initialize_database(); ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        super().__init__(); self.title(APP_NAME); self.geometry("1400x820"); self.minsize(1120,700); self.configure(fg_color=BG_DARK); self.user=None; self.current=None; self.show_login()
    def clear(self):
        for w in self.winfo_children(): w.destroy()
    def show_login(self): self.clear(); LoginView(self,self.show_main)
    def show_main(self,user):
        self.user=user; self.clear(); shell=ctk.CTkFrame(self,fg_color=BG_DARK); shell.pack(fill="both",expand=True)
        sidebar=ctk.CTkFrame(shell,width=235,corner_radius=0,fg_color=PRIMARY); sidebar.pack(side="right",fill="y"); sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar,text="🐟 Azzedine Fish",font=("Tahoma",21,"bold")).pack(pady=(25,4)); ctk.CTkLabel(sidebar,text=f"مرحباً، {user['full_name']}",font=("Tahoma",11),text_color="#A8CAD9").pack(pady=(0,18))
        content=ctk.CTkFrame(shell,fg_color=BG_DARK); content.pack(side="left",fill="both",expand=True,padx=20,pady=20); self.content=content
        pages=[("🏠  الرئيسية",lambda:DashboardPage(content)),("🧾  فاتورة جديدة",lambda:InvoicesPage(content,user)),("📋  سجل الفواتير",lambda:InvoiceHistoryPage(content)),("👥  الزبائن",lambda:CustomersPage(content)),("🚚  الموردون",lambda:SuppliersPage(content)),("📊  التقارير والأرباح",lambda:ReportsPage(content)),("💰  المصاريف",lambda:ExpensesPage(content)),("⚙️  الإعدادات والنسخ",lambda:SettingsPage(content,self))]
        if user["role"]=="مدير": pages.append(("🔐  المستخدمون",lambda:UsersPage(content)))
        for label,factory in pages:
            ctk.CTkButton(sidebar,text=label,command=lambda f=factory:self.open_page(f),anchor="e",font=("Tahoma",13,"bold"),height=42,fg_color="transparent",hover_color=ACCENT,corner_radius=7).pack(fill="x",padx=12,pady=2)
        ctk.CTkButton(sidebar,text="تسجيل الخروج",command=self.show_login,fg_color="#A33A3A",hover_color="#842E2E",font=("Tahoma",13,"bold")).pack(side="bottom",fill="x",padx=15,pady=20)
        self.open_page(lambda:DashboardPage(content))
    def open_page(self,factory):
        if self.current: self.current.destroy()
        self.current=factory(); self.current.pack(fill="both",expand=True)
