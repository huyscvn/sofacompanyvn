from odoo import fields, models, api


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    @api.model
    def create(self, vals):
        program = super(SaleCouponProgram, self).create(vals)
        program.discount_line_product_id.sudo().is_discount = True
        return program

    def write(self, vals):
        res = super(SaleCouponProgram, self).write(vals)
        self.discount_line_product_id.sudo().is_discount = True
        return res

