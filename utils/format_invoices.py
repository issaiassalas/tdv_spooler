import json

def format_payments(invoice):
    invoice_total = invoice.get('amount_total')
    payment_filter = 'inbound'
    if invoice.get('type') == 'out_refund':
        payment_filter = 'outbound'

    valid_payments = list(
        filter(
            lambda payment: payment.get('type') == payment_filter,
            invoice.get('payment')
        )
    )

    result = [
        {
            'id': payment.get('id'),
            'amount': payment.get('amount'),
        } for payment in valid_payments
    ]

    diff = invoice_total - sum(r.get('amount') for r in result)

    if diff > 0:
        result.append({'amount':diff, 'id': 2})

    return result
    

def format_invoices(invoices):
    return [
        {
            'ref_id': invoice.get('id'),
            'name': invoice.get('name'),
            'ticket_ref': invoice.get('ticket_ref'),
            'cn_ticket_ref': invoice.get('cn_ticket_ref'),
            'num_report_z': invoice.get('num_report_z'),
            'fp_serial_num': invoice.get('fp_serial_num'),
            'fp_serial_date': invoice.get('fp_serial_date'),
            'invoice_type': invoice.get('type'),
            'state': 'PENDING',
            'action_type': invoice.get('action_type'),
            'data': json.dumps({
                'client': {
                    'name': invoice.get('partner_id', {}).get('name', 'CLIENTEXXX'),
                    'ced_rif': invoice.get('partner_id', {}).get('vat', '00000001'),
                    'street': invoice.get('partner_id', {}).get('street', 'XXX, XXX'),
                    'phone': invoice.get('partner_id', {}).get('phone', '0286XXXXXXX')
                },
                'products': [
                    {
                        'name': product.get('name'),
                        'price_unit': product.get('price_unit'),
                        'product_qty': product.get('product_qty'),
                        'tax': product.get('tax_ids'),
                    }
                    for product in invoice.get('invoice_line_ids')
                ],
                'payments': format_payments(invoice),
                'reversed': invoice.get('reversed')
            }),
            'amount_total': invoice.get('amount_total')
        } for invoice in invoices
    ]