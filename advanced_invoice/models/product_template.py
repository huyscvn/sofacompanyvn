# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_delivery = fields.Boolean(string='Delivery product', default=False)

    @api.onchange('x_product_function_id')
    def onchange_x_product_function_id(self):
        for rec in self:
            if rec.x_product_function_id:
                rec.x_category_ids = [(4, value, 0) for value in rec.x_product_function_id.x_function_category.ids]

    # @api.model
    # def create(self, vals_list):
    #     result = super(ProductTemplate, self).create(vals_list)
    #     if result.x_product_function_id:
    #         result.x_category_ids = [(4, value, 0) for value in result.x_product_function_id.x_function_category.ids]
    #     return result

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_cost = fields.Float(string="phí vận chuyển",
                                                compute='compute_delivery_cost',
                                                compute_sudo=True,store=True)
    @api.depends('order_line')
    def compute_delivery_cost(self):
        for rec in self:
            rec.delivery_cost = 0
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.is_delivery:
                    rec.delivery_cost += line.price_subtotal


class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_cost = fields.Float(string="phí vận chuyển",
                                 compute='compute_delivery_cost',
                                 compute_sudo=True, store=True)
    sale_order_id = fields.Many2one('sale.order', compute='_get_sale_order', store=True)
    picking_id = fields.Many2one('stock.picking', compute='_get_picking_id', store=True)


    @api.depends('invoice_line_ids')
    def compute_delivery_cost(self):
        for rec in self:
            rec.delivery_cost = 0
            for line in rec.invoice_line_ids:
                if line.product_id.product_tmpl_id.is_delivery:
                    rec.delivery_cost += line.price_subtotal

    @api.depends('invoice_line_ids.sale_line_ids')
    def _get_sale_order(self):
        for invoice in self:
            invoice.sale_order_id = False
            order = self.env['sale.order'].sudo().search([('invoice_ids', '=', invoice.id)], limit=1).id
            if order:
                invoice.sale_order_id = order

    @api.depends('sale_order_id.picking_ids.state')
    def _get_picking_id(self):
        for invoice in self:
            invoice.picking_id = False
            picking = self.env['stock.picking'].sudo().search(
                [('id', 'in', invoice.sale_order_id.picking_ids.ids), ('state', 'not in', ['cancel'])], limit=1).id
            if picking:
                invoice.picking_id = picking

