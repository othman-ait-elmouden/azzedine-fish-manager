from pathlib import Path
import os, tempfile
import qrcode
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.graphics.shapes import Drawing, Circle, Ellipse, Polygon, String
from database.connection import db
from config import EXPORT_DIR

NAVY=colors.HexColor("#0B3954"); TURQUOISE=colors.HexColor("#00A6A6")
PALE=colors.HexColor("#EAF7F7"); BORDER=colors.HexColor("#B7CDD5")

def _font():
    for path in [r"C:\Windows\Fonts\tahoma.ttf",r"C:\Windows\Fonts\arial.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(path).exists():
            try: pdfmetrics.registerFont(TTFont("Arabic",path)); return "Arabic"
            except Exception: pass
    return "Helvetica"

def _rtl(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except ImportError: return str(text)

def _default_logo():
    d=Drawing(105,58)
    d.add(Circle(29,29,26,fillColor=NAVY,strokeColor=TURQUOISE,strokeWidth=2))
    d.add(Ellipse(30,31,30,13,fillColor=TURQUOISE,strokeColor=None))
    d.add(Polygon([4,31,15,41,15,21],fillColor=TURQUOISE,strokeColor=None))
    d.add(Circle(40,34,1.6,fillColor=colors.white,strokeColor=None))
    d.add(String(61,33,"AZZEDINE",fontName="Helvetica-Bold",fontSize=8,fillColor=NAVY))
    d.add(String(61,20,"FISH",fontName="Helvetica-Bold",fontSize=12,fillColor=TURQUOISE))
    return d

def generate_invoice_pdf(invoice, items, paper="A4", output=None):
    settings={r["key"]:r["value"] for r in db.query("SELECT * FROM settings")}
    sizes={"A4":A4,"80mm":(80*mm,240*mm),"58mm":(58*mm,240*mm)}
    page=sizes.get(paper,A4); compact=paper!="A4"; margin=12*mm if not compact else 4*mm
    output=Path(output or EXPORT_DIR/f"{invoice['invoice_no']}.pdf")
    doc=SimpleDocTemplate(str(output),pagesize=page,rightMargin=margin,leftMargin=margin,topMargin=margin,bottomMargin=margin)
    font=_font(); base=getSampleStyleSheet()["Normal"]
    normal=ParagraphStyle("ar",parent=base,fontName=font,fontSize=7.2 if compact else 9.5,leading=10 if compact else 14,alignment=TA_RIGHT,textColor=NAVY)
    title=ParagraphStyle("title",parent=normal,fontSize=13 if compact else 20,leading=17 if compact else 25,alignment=TA_CENTER,textColor=NAVY)
    small=ParagraphStyle("small",parent=normal,fontSize=6.5 if compact else 8,leading=9 if compact else 11,alignment=TA_CENTER,textColor=colors.HexColor("#56717E"))
    logo_path=settings.get("logo","")
    logo=Image(logo_path,width=24*mm,height=24*mm) if logo_path and Path(logo_path).exists() else _default_logo()
    shop=Paragraph(f"<b>{_rtl(settings.get('shop_name','Azzedine Fish'))}</b><br/><font color='#56717E'>{_rtl(settings.get('address',''))}<br/>{_rtl('الهاتف')}: {settings.get('phone','')}</font>",title)
    story=[]
    if compact: story.extend([logo,shop,Spacer(1,2*mm)])
    else:
        header=Table([[shop,logo]],colWidths=[page[0]-2*margin-40*mm,40*mm],hAlign="RIGHT")
        header.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(1,0),(1,0),"RIGHT"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])); story.append(header)
    story.extend([Spacer(1,2*mm),HRFlowable(width="100%",thickness=2,color=TURQUOISE,spaceAfter=4*mm)])
    customer=invoice["customer_name"] or "زبون نقدي"
    info=[[Paragraph(_rtl(f"رقم الفاتورة: {invoice['invoice_no']}"),normal),Paragraph(_rtl(f"الزبون: {customer}"),normal)],[Paragraph(_rtl(f"طريقة الدفع: {invoice['payment_method']}"),normal),Paragraph(_rtl(f"التاريخ: {invoice['created_at']}"),normal)]]
    info_table=Table(info,colWidths=[(page[0]-2*margin)/2]*2)
    info_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PALE),("BOX",(0,0),(-1,-1),.7,TURQUOISE),("INNERGRID",(0,0),(-1,-1),.35,BORDER),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)])); story.extend([info_table,Spacer(1,4*mm)])
    data=[[_rtl(x) for x in ("المجموع","السعر","الكمية","المنتج")]]
    for item in items: data.append([f"{item['total']:.2f}",f"{item['unit_price']:.2f}",f"{item['quantity']:g}",_rtl(item["product_name"])])
    available=page[0]-2*margin
    widths=[available*.20,available*.20,available*.16,available*.44] if not compact else [15*mm,13*mm,10*mm,available-38*mm]
    product_table=Table(data,colWidths=widths,repeatRows=1)
    commands=[("FONTNAME",(0,0),(-1,-1),font),("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("LINEBELOW",(0,0),(-1,0),2,TURQUOISE),("GRID",(0,0),(-1,-1),.35,BORDER),("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("FONTSIZE",(0,0),(-1,-1),7 if compact else 9),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]
    for row in range(2,len(data),2): commands.append(("BACKGROUND",(0,row),(-1,row),colors.HexColor("#F1F8FA")))
    product_table.setStyle(TableStyle(commands)); story.extend([product_table,Spacer(1,4*mm)])
    cur=settings.get("currency","د.م")
    totals=[[f"{invoice['subtotal']:.2f} {cur}",_rtl("المجموع الفرعي")],[f"{invoice['discount']:.2f} {cur}",_rtl("الخصم")],[f"{invoice['tax']:.2f} {cur}",_rtl("الضريبة")],[f"{invoice['total']:.2f} {cur}",_rtl("المجموع النهائي")]]
    total_table=Table(totals,colWidths=[32*mm,38*mm],hAlign="CENTER" if compact else "LEFT")
    total_table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),font),("ALIGN",(0,0),(-1,-1),"CENTER"),("GRID",(0,0),(-1,-1),.4,BORDER),("BACKGROUND",(0,-1),(-1,-1),TURQUOISE),("TEXTCOLOR",(0,-1),(-1,-1),colors.white),("FONTSIZE",(0,0),(-1,-1),8 if compact else 10),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)])); story.append(total_table)
    qr=qrcode.make(f"{invoice['invoice_no']}|{invoice['total']:.2f}"); tmp=Path(tempfile.gettempdir())/f"qr_{invoice['id']}.png"; qr.save(tmp)
    story.extend([Spacer(1,4*mm),Image(str(tmp),width=20*mm,height=20*mm),Paragraph(_rtl("شكراً لاختياركم Azzedine Fish"),title),Paragraph(_rtl("جودة البحر... بين أيديكم"),small),Spacer(1,2*mm),HRFlowable(width="100%",thickness=1,color=TURQUOISE)])
    doc.build(story)
    try: tmp.unlink()
    except OSError: pass
    return output

def print_file(path):
    if os.name=="nt": os.startfile(str(path),"print")
    else: os.system(f"lp '{path}'")
