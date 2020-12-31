from odoo import fields, models, api
import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_cost = fields.Float(string="phí vận chuyển",
                                 compute='compute_delivery_cost',
                                 compute_sudo=True, store=True)
    discount_compute = fields.Float(string="Tổng tiền giảm giá",
                                    compute='compute_discount',
                                    compute_sudo=True, store=True)
    sale_order_id = fields.Many2one('sale.order', compute='_get_sale_order', store=True)
    # picking_ids = fields.Many2one('stock.picking', compute='_get_picking_id', store=True)
    picking = fields.Char(compute='_get_picking_id')
    picking_date = fields.Char(compute='_get_picking_id')
    inventory_fees_order_id = fields.Many2one('sale.order')
    is_inventory_fees = fields.Boolean("Là phí lưu kho")

    @api.depends('invoice_line_ids')
    def compute_delivery_cost(self):
        for rec in self:
            rec.delivery_cost = 0
            for line in rec.invoice_line_ids:
                if line.product_id.product_tmpl_id.is_delivery:
                    rec.delivery_cost += line.price_subtotal

    @api.depends('invoice_line_ids')
    def compute_discount(self):
        for rec in self:
            rec.discount_compute = 0
            for line in rec.invoice_line_ids:
                if line.product_id.product_tmpl_id.is_discount:
                    rec.discount_compute += abs(line.price_subtotal)

    @api.depends('invoice_line_ids.sale_line_ids', 'inventory_fees_order_id')
    def _get_sale_order(self):
        for invoice in self:
            invoice.sale_order_id = False
            if not invoice.is_inventory_fees:
                order = self.env['sale.order'].sudo().search([('invoice_ids', '=', invoice.id)], limit=1).id
                if order:
                    invoice.sale_order_id = order
            else:
                if invoice.inventory_fees_order_id:
                    invoice.sale_order_id = invoice.inventory_fees_order_id.id

    @api.depends('sale_order_id.picking_ids.state')
    def _get_picking_id(self):
        for invoice in self:
            invoice.picking = ''
            invoice.picking_date = ''
            string = ''
            date_string = ''
            picking = self.env['stock.picking'].sudo().search(
                [('id', 'in', invoice.sale_order_id.picking_ids.ids), ('state', 'not in', ['cancel'])])
            if picking:
                for p in picking:
                    string += p.name + ', '
                    date_string += datetime.datetime.strftime(p.scheduled_date, '%d-%m-%Y') + ', '
                invoice.picking = string[:-2]
                invoice.picking_date = date_string[:-2]

