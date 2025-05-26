# /home/ubuntu/platform-services/invoicing_service/models.py
# Autor: Szymon Fuchs
# Data: 27.08.2021

from django.db import models

class Invoice(models.Model):
    saleor_order_id = models.CharField(max_length=255, unique=True)
    user_email = models.EmailField()
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    buyer_name = models.CharField(max_length=255)
    buyer_address = models.TextField()
    buyer_nip = models.CharField(max_length=20, blank=True, null=True)
    pdf_file_path = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.saleor_order_id}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=4, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"
