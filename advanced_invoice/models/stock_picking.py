from odoo import fields, models, api
from odoo.exceptions import UserError
import requests

class StockPicking(models.Model):
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
    
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for rec in self:
            if rec.state == 'done':
                if rec.sale_id:
                    template = self.env.ref('advanced_invoice.mail_template_data_delivery_confirm',
                                            raise_if_not_found=False)
                    if template:
                        template.send_mail(rec.id, force_send=True, raise_exception=False)
                    if rec.sale_id.x_studio_mobile:
                        phone = str(rec.sale_id.x_studio_mobile)
                        bid = rec.sale_id.name
                        sms = " Don hang ["+rec.sale_id.name+"] da duoc giao thanh cong. Chuc quy khach co trai nghiem tot voi SOFACOMPANY"
                        url = "https://cloudsms4.vietguys.biz:4438/api/index.php?u=sofacompany&pwd=28ruv&from=SOFACOMPANY&phone=%s&sms=%s&bid=%s&type=8&json=1" % (
                            phone, sms, bid)
                        payload = {}
                        headers = {}
                        try:
                            res = requests.request("POST", url, headers=headers, data=payload)
                            print(res.json())
                        except:
                            e = 0
        return res
