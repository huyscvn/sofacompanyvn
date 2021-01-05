from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

class CreateInventoryFeeInvoice(models.TransientModel):
    _name = 'create.inventory.fee.invoice'

    sale_order_id = fields.Many2one('sale.order')
    stock_picking_id = fields.Many2one('stock.picking')
    scheduled_date = fields.Date('Ngày giao hàng dự kiến')
    predicted_date = fields.Date('Ngày giao hàng mới')
    inventory_fee = fields.Float('Chi phí lưu kho dự kiến', compute="compute_inventory_fee")
    days_late = fields.Integer('Số ngày trễ', compute="compute_inventory_fee")

    @api.depends('predicted_date')
    def compute_inventory_fee(self):
        self.inventory_fee = 0
        self.days_late = 0
        if self.predicted_date:
            scheduled = self.sudo().stock_picking_id.scheduled_date
            total = self.sudo().sale_order_id.amount_total
            scheduled_date_timezone = pytz.utc.localize(scheduled) + relativedelta(hours=7)
            now_date = self.predicted_date
            scheduled_date = scheduled_date_timezone.date()
            days_late = int((now_date - scheduled_date).days) - 7
            if days_late > 0:
                self.inventory_fee = round(total * days_late * 0.5 / 100, -3)
                self.days_late = days_late

    def create_inventory_fee_invoice(self):
        product_id = self.env.ref('advanced_invoice.product_product_inventory_fees')
        journal_id = self.env['account.journal'].sudo().search([('type', '=', 'sale')],
                                                               limit=1).id
        data = {
            'product_id': product_id.sudo().id,
            'name': product_id.sudo().name,
            'quantity': 1,
            'price_unit': self.inventory_fee,
            'product_uom_id': product_id.sudo().uom_id.id
        }
        invoice_id = self.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': self.sudo().sale_order_id.partner_id.id,
            'inventory_fees_order_id': self.sudo().sale_order_id.id,
            'is_inventory_fees': True,
            'journal_id': journal_id,
            'narration': "Hóa đơn tính phí lưu kho trễ " + str(self.days_late) + " ngày của đơn hàng " + str(self.sudo().sale_order_id.name)
        })
        invoice_id.invoice_line_ids = [(0, 0, data)]
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = invoice_id.id
        return action