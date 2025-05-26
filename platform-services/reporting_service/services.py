# /home/ubuntu/platform-services/reporting_service/services.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

from .graphql_client import SaleorGraphQLClient
from .queries import ORDERS_QUERY, PRODUCT_PERFORMANCE_QUERY
from collections import defaultdict
from django.utils import timezone

async def _fetch_all_saleor_data(query, variables, max_pages=100):
    client = SaleorGraphQLClient()
    all_edges = []
    has_next_page = True
    current_page = 0

    while has_next_page and current_page < max_pages:
        response_data = await client.execute(query, variables)
        if response_data.get('errors'):
            return {"error": "Saleor API Error", "details": response_data['errors']}

        data_key = None
        if 'orders' in response_data.get('data', {}):
            data_key = 'orders'
        elif 'products' in response_data.get('data', {}):
            data_key = 'products'
        
        if not data_key or not response_data['data'][data_key]:
            break 
            
        page_data = response_data['data'][data_key]
        all_edges.extend(page_data.get('edges', []))
        
        page_info = page_data.get('pageInfo', {})
        has_next_page = page_info.get('hasNextPage', False)
        variables['after'] = page_info.get('endCursor')
        current_page += 1
        if not variables['after']:
            has_next_page = False
            
    return all_edges


async def get_sales_report_for_channel(user_id, channel_slug, date_from, date_to):
    variables = {
        "channel": channel_slug,
        "createdGte": date_from.isoformat() + "T00:00:00+00:00",
        "createdLte": date_to.isoformat() + "T23:59:59+00:00",
        "first": 100,
        "after": None
    }
    
    all_order_edges = await _fetch_all_saleor_data(ORDERS_QUERY, variables)

    if isinstance(all_order_edges, dict) and "error" in all_order_edges:
        return all_order_edges

    total_sales_amount = 0
    order_count = len(all_order_edges)
    orders_summary = []

    for edge in all_order_edges:
        node = edge.get('node', {})
        total_sales_amount += node.get('total', {}).get('gross', {}).get('amount', 0)
        orders_summary.append({
            "number": node.get('number'),
            "amount": node.get('total', {}).get('gross', {}).get('amount', 0),
            "status": node.get('status'),
            "created_at": node.get('created')
        })
    
    report = {
        "report_type": "SalesSummary",
        "generated_at": timezone.now().isoformat(),
        "channel": channel_slug,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "total_sales_amount": round(total_sales_amount, 2),
        "order_count": order_count,
        "orders_summary": orders_summary
    }
    return report

async def get_product_performance_report(user_id, channel_slug, date_from, date_to, top_n=10):
    variables = {
        "channel": channel_slug,
        "createdGte": date_from.isoformat() + "T00:00:00+00:00",
        "createdLte": date_to.isoformat() + "T23:59:59+00:00",
        "first": 100,
        "after": None
    }

    all_order_edges = await _fetch_all_saleor_data(PRODUCT_PERFORMANCE_QUERY, variables)

    if isinstance(all_order_edges, dict) and "error" in all_order_edges:
        return all_order_edges

    product_sales = defaultdict(lambda: {'quantity': 0, 'total_amount': 0.0})

    for edge in all_order_edges:
        order_node = edge.get('node', {})
        for line in order_node.get('lines', []):
            sku = line.get('productSku') or line.get('variantName') or line.get('productName', 'Unknown Product')
            product_sales[sku]['quantity'] += line.get('quantity', 0)
            product_sales[sku]['total_amount'] += line.get('totalPrice', {}).get('gross', {}).get('amount', 0)
            if 'product_name' not in product_sales[sku]:
                 product_sales[sku]['product_name'] = line.get('productName', 'N/A')
            if 'variant_name' not in product_sales[sku]:
                 product_sales[sku]['variant_name'] = line.get('variantName', 'N/A')


    sorted_products = sorted(product_sales.items(), key=lambda item: item[1]['total_amount'], reverse=True)
    
    report_products = []
    for sku, data in sorted_products[:top_n]:
        report_products.append({
            "sku": sku,
            "product_name": data.get('product_name'),
            "variant_name": data.get('variant_name'),
            "quantity_sold": data['quantity'],
            "total_sales_amount": round(data['total_amount'], 2)
        })

    report = {
        "report_type": "ProductPerformance",
        "generated_at": timezone.now().isoformat(),
        "channel": channel_slug,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "top_n_products": report_products
    }
    return report
