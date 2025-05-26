# /home/ubuntu/platform-services/invoicing_service/invoice_generator.py
# Autor: Szymon Fuchs
# Data: 28.08.2021

from django.conf import settings
import os
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm

def generate_next_invoice_number(issue_date):
    from .models import Invoice
    current_year = issue_date.year
    current_month = issue_date.month
    last_invoice = Invoice.objects.filter(
        issue_date__year=current_year,
        issue_date__month=current_month
    ).order_by('invoice_number').last()

    if last_invoice and last_invoice.invoice_number:
        try:
            parts = last_invoice.invoice_number.split('/')
            last_seq = int(parts[-1])
            new_seq = last_seq + 1
        except (IndexError, ValueError):
            new_seq = 1
    else:
        new_seq = 1
    return f"{current_month:02d}/{current_year}/{new_seq:03d}"


def generate_invoice_pdf(invoice_data, items_data):
    invoices_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoices_dir, exist_ok=True)
    
    filename = f"{invoice_data.invoice_number.replace('/', '_')}.pdf"
    pdf_path_on_disk = os.path.join(invoices_dir, filename)
    pdf_url_path = os.path.join(settings.MEDIA_URL, 'invoices', filename)
    
    print(f"generowanie PDF dla faktury: {invoice_data.invoice_number} do {pdf_path_on_disk}")
    # Tutaj logika z ReportLab lub WeasyPrint
    # p = canvas.Canvas(pdf_path_on_disk, pagesize=A4)
    # p.drawString(72, 72*10, f"Faktura nr: {invoice_data.invoice_number}")
    # p.save()
    with open(pdf_path_on_disk, 'w') as f:
        f.write(f"Placeholder for Invoice {invoice_data.invoice_number}")

    return pdf_url_path
