# /home/ubuntu/platform-services/invoicing_service/webhook_handlers.py
# Autor: Szymon Fuchs
# Data: 30.08.2021

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json
from decimal import Decimal

from .models import Invoice, InvoiceItem
from .invoice_generator import generate_next_invoice_number, generate_invoice_pdf

@csrf_exempt
@require_POST
def saleor_order_to_invoice_webhook(request):
    try:
        payload = json.loads(request.body)
        order_id_from_saleor = payload.get('id') 
        user_email_from_saleor = payload.get('user_email')
        billing_address_data = payload.get('billing_address', {})
        lines_data = payload.get('lines', [])
        total_gross_amount = Decimal(payload.get('total', {}).get('gross', {}).get('amount', '0.0'))
        currency = payload.get('total', {}).get('gross', {}).get('currency', 'PLN')

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not all([order_id_from_saleor, user_email_from_saleor, lines_data]):
         return JsonResponse({'error': 'Missing critical order data in webhook for invoicing'}, status=400)

    if Invoice.objects.filter(saleor_order_id=order_id_from_saleor).exists():
        return HttpResponse('Invoice already exists for this order.', status=200)

    issue_date = timezone.now().date()
    invoice_number = generate_next_invoice_number(issue_date)
    
    buyer_name = billing_address_data.get('company_name', 
                    f"{billing_address_data.get('first_name', '')} {billing_address_data.get('last_name', '')}".strip())
    buyer_address_parts = [
        billing_address_data.get('street_address_1'),
        billing_address_data.get('street_address_2'),
        f"{billing_address_data.get('postal_code', '')} {billing_address_data.get('city', '')}",
        billing_address_data.get('country', {}).get('country')
    ]
    buyer_full_address = "\n".join(filter(None, buyer_address_parts))
    buyer_nip_from_metadata = billing_address_data.get('vat_id', None)

    invoice = Invoice.objects.create(
        saleor_order_id=order_id_from_saleor,
        user_email=user_email_from_saleor,
        invoice_number=invoice_number,
        issue_date=issue_date,
        due_date=issue_date + timedelta(days=14),
        total_amount=total_gross_amount,
        currency=currency,
        buyer_name=buyer_name,
        buyer_address=buyer_full_address,
        buyer_nip=buyer_nip_from_metadata
    )

    for line in lines_data:
        InvoiceItem.objects.create(
            invoice=invoice,
            product_name=line.get('product_name'),
            quantity=line.get('quantity', 1),
            unit_price=Decimal(line.get('unit_price', {}).get('gross', {}).get('amount', '0.0')),
            net_amount=Decimal(line.get('total_price', {}).get('net', {}).get('amount', '0.0')),
            vat_rate=Decimal(line.get('tax_rate', '0.0')) * 100,
            vat_amount=Decimal(line.get('total_price', {}).get('tax', {}).get('amount', '0.0')),
            gross_amount=Decimal(line.get('total_price', {}).get('gross', {}).get('amount', '0.0'))
        )
    
    pdf_url = generate_invoice_pdf(invoice, invoice.items.all())
    if pdf_url:
        invoice.pdf_file_path = pdf_url # Zapisujemy URL, nie ścieżkę dyskową
        invoice.save(update_fields=['pdf_file_path'])
        
    return HttpResponse(f'Invoice {invoice_number} created successfully.', status=201)
