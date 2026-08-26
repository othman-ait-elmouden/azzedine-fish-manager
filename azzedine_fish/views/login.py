import customtkinter as ctk
from tkinter import messagebox
from config import PRIMARY,ACCENT,BG_DARK
from services.auth_service import AuthService
from views.widgets import button

class LoginView(ctk.CTkFrame):
    def __init__(self,master,on_success):
        super().__init__(master,fg_color=BG_DARK); self.pack(fill="both",expand=True); self.on_success=on_success
        card=ctk.CTkFrame(self,width=430,height=500,corner_radius=24,fg_color=PRIMARY); card.place(relx=.5,rely=.5,anchor="center"); card.pack_propagate(False)
        ctk.CTkLabel(card,text="🐟",font=("Segoe UI Emoji",65)).pack(pady=(35,5))
        ctk.CTkLabel(card,text="Azzedine Fish",font=("Tahoma",28,"bold")).pack()
        ctk.CTkLabel(card,text="نظام إدارة محل الأسماك",font=("Tahoma",14),text_color="#B8D8E8").pack(pady=(5,25))
        self.username=ctk.CTkEntry(card,placeholder_text="اسم المستخدم",justify="right",height=44,font=("Tahoma",14)); self.username.pack(fill="x",padx=55,pady=8)
        self.password=ctk.CTkEntry(card,placeholder_text="كلمة المرور",show="●",justify="right",height=44,font=("Tahoma",14)); self.password.pack(fill="x",padx=55,pady=8)
        button(card,"تسجيل الدخول",self.login).pack(fill="x",padx=55,pady=(18,8))
        ctk.CTkButton(card,text="تغيير كلمة المرور",command=self.change_password,fg_color="transparent",border_width=1,font=("Tahoma",12)).pack(fill="x",padx=55,pady=4)
        ctk.CTkLabel(card,text="الدخول الأول: admin / admin123",font=("Tahoma",11),text_color="#9DB6C3").pack(pady=8)
        self.password.bind("<Return>",lambda e:self.login()); self.username.focus()
    def login(self):
        user=AuthService.login(self.username.get(),self.password.get())
        if user: self.on_success(user)
        else: messagebox.showerror("خطأ","اسم المستخدم أو كلمة المرور غير صحيحة")
    def change_password(self):
        dialog=ctk.CTkToplevel(self); dialog.title("تغيير كلمة المرور"); dialog.geometry("400x360"); dialog.grab_set()
        ctk.CTkLabel(dialog,text="تغيير كلمة المرور",font=("Tahoma",20,"bold")).pack(pady=18)
        entries=[]
        for placeholder,show in (("اسم المستخدم",None),("كلمة المرور الحالية","●"),("كلمة المرور الجديدة","●"),("تأكيد كلمة المرور الجديدة","●")):
            e=ctk.CTkEntry(dialog,placeholder_text=placeholder,show=show or "",justify="right",height=40); e.pack(fill="x",padx=35,pady=5); entries.append(e)
        def save():
            user=AuthService.login(entries[0].get(),entries[1].get())
            if not user: return messagebox.showerror("خطأ","البيانات الحالية غير صحيحة",parent=dialog)
            if len(entries[2].get())<6: return messagebox.showerror("خطأ","كلمة المرور الجديدة يجب أن تكون 6 أحرف على الأقل",parent=dialog)
            if entries[2].get()!=entries[3].get(): return messagebox.showerror("خطأ","كلمتا المرور غير متطابقتين",parent=dialog)
            AuthService.change_password(user["id"],entries[1].get(),entries[2].get()); messagebox.showinfo("تم","تم تغيير كلمة المرور",parent=dialog); dialog.destroy()
        button(dialog,"حفظ",save).pack(fill="x",padx=35,pady=16)
