from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_format_discount_unit_price(self):
        if self.discount:
            price_unit = (100 - self.discount) * self.price_unit / 100
            price_unit = "{0:,.0f}".format(price_unit)
            return price_unit
        else:
            return 0

    def get_format_unit_price(self):
        if self.price_unit:
            price_unit = self.price_unit
            price_unit = "{0:,.0f}".format(price_unit)
            return price_unit
        else:
            return 0

    def get_format_price_subtotal(self):
        if self.price_subtotal:
            price_subtotal = "{0:,.0f}".format(self.price_subtotal)
            return price_subtotal
        else:
            return 0
