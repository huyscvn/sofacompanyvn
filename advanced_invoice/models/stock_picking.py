from odoo import fields, models, api
from odoo.exceptions import UserError


class ModelName (models.Model):
    _inherit = 'stock.picking'

    def do_print_invoice(self):
        if self.sale_id:
            invoice = self.env['account.move'].sudo().search(
                [('sale_order_id', '=', self.sale_id.id), ('state', 'not in', ['cancel'])], limit=1)
            if len(invoice) > 0:
                return self.env.ref('advanced_invoice.action_print_advanced_invoice').report_action(invoice)
            else:
                raise UserError("Can't find invoice to print")
        else:
            raise UserError("Can't find invoice to print")
    


