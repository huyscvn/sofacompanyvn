# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
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
                                 compute_sudo=True, store=True)

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

    def get_format_amount_untaxed(self):
        if self.amount_untaxed:
            amount_untaxed = self.amount_untaxed
            amount_untaxed = "{0:,.0f}".format(amount_untaxed)
            return amount_untaxed

    def get_format_amount_total(self):
        if self.amount_total:
            amount_total = "{0:,.0f}".format(self.amount_total)
            return amount_total

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        template = self.env.ref('advanced_invoice.mail_template_data_sale_order_confirm', raise_if_not_found=False)
        for order in self:
            if template:
                template.send_mail(order.id, force_send=True, raise_exception=False)
            if order.x_studio_mobile:
                phone = str(order.x_studio_mobile)
                bid = order.name
                sms = "Cam on quy khach da dat hang tai SOFACOMPANY. Ma don hang [" + order.name + "] tri gia [" + order.get_format_amount_total() + "]đ. CSKH: 1900636845 (10:00 - 18:00)"
                url = "https://cloudsms.vietguys.biz:4438/api/index.php?u=sofacompany&pwd=28ruv&from=SOFACOMPANY&phone=%s&sms=%s&bid=%s&type=8&json=1" % (
                phone, sms, bid)
                payload = {}
                headers = {}
                try:
                    requests.request("POST", url, headers=headers, data=payload)
                except:
                    e = 0
        return res


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
