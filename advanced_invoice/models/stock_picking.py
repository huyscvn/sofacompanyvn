from odoo import fields, models, api
from odoo.exceptions import UserError
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    count_inventory_fees_invoice = fields.Integer(string="Hóa đơn phí lưu kho",
                                                  compute="compute_count_inventory_fees_invoice")
    picking_type_code = fields.Selection(related='picking_type_id.code')

    def compute_count_inventory_fees_invoice(self):
        for rec in self:
            rec.count_inventory_fees_invoice = 0
            invoices = self.env['account.move'].sudo().search(
                [('sale_order_id', '=', rec.sale_id.id), ('is_inventory_fees', '=', True)])
            rec.count_inventory_fees_invoice = len(invoices)

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

    def action_open_inventory_fees_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('sale_order_id', '=', self.sale_id.id), ('is_inventory_fees', '=', True)]
        action['context'] = {'create': False, 'edit': True}
        return action


    def create_inventory_fee_invoice(self):
        return {
            'name': ("Tạo hóa đơn phí lưu kho"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'create.inventory.fee.invoice',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.sudo().sale_id.id,
                'default_stock_picking_id': self.id,
                'default_scheduled_date': self.scheduled_date.date(),
            }
        }

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'date_done' in vals:
            now = datetime.now()
            for rec in self:
                if rec.state == 'done':
                    if rec.sale_id:
                        if rec.picking_type_id.code == 'outgoing':
                            ### TODO gui tin nhan
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
                            ### TODO gui tin nhan
                            if not self.count_inventory_fees_invoice > 0:
                                if rec.scheduled_date:
                                    scheduled = rec.scheduled_date
                                    total = rec.sudo().sale_id.amount_total
                                    # user_tz = 'utc'
                                    # local = pytz.timezone(user_tz)
                                    now_timezone = pytz.utc.localize(now) + relativedelta(hours=7)
                                    scheduled_date_timezone = pytz.utc.localize(scheduled) + relativedelta(hours=7)
                                    now_date = now_timezone.date()
                                    scheduled_date = scheduled_date_timezone.date()
                                    days_late = int((now_date - scheduled_date).days)
                                    if days_late > 0:
                                        inventory_fees = round(total * days_late * 0.5 / 100, -3)
                                        if inventory_fees > 0:
                                            product_id = self.env.ref('advanced_invoice.product_product_inventory_fees')
                                            journal_id = self.env['account.journal'].sudo().search([('type', '=', 'sale')],
                                                                                                   limit=1).id
                                            data = {
                                                'product_id': product_id.sudo().id,
                                                'name': product_id.sudo().name,
                                                'quantity': 1,
                                                'price_unit': inventory_fees,
                                                'product_uom_id': product_id.sudo().uom_id.id
                                            }
                                            invoice_id = self.env['account.move'].create({
                                                'type': 'out_invoice',
                                                'partner_id': rec.sudo().sale_id.partner_id.id,
                                                'inventory_fees_order_id': rec.sudo().sale_id.id,
                                                'is_inventory_fees': True,
                                                'journal_id': journal_id,
                                                'narration': "Hóa đơn tính phí lưu kho trễ " + str(
                                                    days_late) + " ngày của đơn hàng " + str(rec.sudo().sale_id.name)
                                            })
                                            invoice_id.invoice_line_ids = [(0, 0, data)]
                                            print(inventory_fees)
                                    print(days_late)
        return res
