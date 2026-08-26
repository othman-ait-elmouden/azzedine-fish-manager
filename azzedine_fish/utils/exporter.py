import csv
from pathlib import Path
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape

def export_csv(path, headers, rows):
    with open(path,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(headers); w.writerows(rows)
    return Path(path)

def export_excel(path, headers, rows, title="تقرير"):
    wb=Workbook(); ws=wb.active; ws.title=title; ws.sheet_view.rightToLeft=True
    ws.append(headers)
    for row in rows: ws.append(list(row))
    for cell in ws[1]: cell.font=cell.font.copy(bold=True); cell.fill=cell.fill.copy(fgColor="00A6A6",fill_type="solid")
    ws.freeze_panes="A2"; wb.save(path); return Path(path)

def export_pdf_table(path, headers, rows):
    doc=SimpleDocTemplate(str(path),pagesize=landscape(A4)); t=Table([headers]+[list(r) for r in rows],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#00A6A6")),("GRID",(0,0),(-1,-1),.5,colors.grey),("ALIGN",(0,0),(-1,-1),"CENTER")]))
    doc.build([t]); return Path(path)

