import customtkinter as ctk
from tkinter import ttk
from config import ACCENT,ACCENT_HOVER,CARD_DARK,TEXT,MUTED

def button(parent,text,command=None,**kw):
    return ctk.CTkButton(parent,text=text,command=command,fg_color=kw.pop("fg_color",ACCENT),hover_color=ACCENT_HOVER,font=("Tahoma",14,"bold"),height=38,**kw)

class StatCard(ctk.CTkFrame):
    def __init__(self,parent,title,value,icon="📊"):
        super().__init__(parent,fg_color=CARD_DARK,corner_radius=14)
        ctk.CTkLabel(self,text=icon,font=("Segoe UI Emoji",28)).pack(anchor="e",padx=15,pady=(12,0))
        ctk.CTkLabel(self,text=title,font=("Tahoma",13),text_color=MUTED).pack(anchor="e",padx=15)
        ctk.CTkLabel(self,text=str(value),font=("Tahoma",22,"bold"),text_color=TEXT).pack(anchor="e",padx=15,pady=(2,14))

class DataTable(ctk.CTkFrame):
    def __init__(self,parent,columns,headings):
        super().__init__(parent,fg_color="transparent")
        style=ttk.Style(); style.theme_use("clam")
        style.configure("Treeview",background="#102F40",foreground="white",fieldbackground="#102F40",rowheight=32,font=("Tahoma",11))
        style.configure("Treeview.Heading",background="#0B3954",foreground="white",font=("Tahoma",11,"bold"))
        self.tree=ttk.Treeview(self,columns=columns,show="headings",selectmode="browse")
        for c,h in zip(columns,headings): self.tree.heading(c,text=h); self.tree.column(c,anchor="center",width=110)
        self.tree.pack(fill="both",expand=True)
    def fill(self,rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows: self.tree.insert("", "end", values=row)
    def selected_id(self):
        s=self.tree.selection(); return self.tree.item(s[0],"values")[0] if s else None

