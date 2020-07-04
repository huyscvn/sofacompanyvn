# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_delivery = fields.Boolean(string='Delivery product', default=False)
    is_discount = fields.Boolean(string='Discount product', default=False)

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

    discount_compute = fields.Float(string="Tổng tiền giảm giá",
                                 compute='compute_discount',
                                 compute_sudo=True, store=True)
    @api.depends('order_line')
    def compute_delivery_cost(self):
        for rec in self:
            rec.delivery_cost = 0
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.is_delivery:
                    rec.delivery_cost += line.price_subtotal

    @api.depends('order_line')
    def compute_discount(self):
        for rec in self:
            rec.discount_compute = 0
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.is_discount:
                    rec.discount_compute += abs(line.price_subtotal)


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


