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






