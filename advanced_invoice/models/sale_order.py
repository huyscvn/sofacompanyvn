from odoo import fields, models, api
import requests
import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_cost = fields.Float(string="phí vận chuyển",
                                 compute='compute_delivery_cost',
                                 compute_sudo=True, store=True)

    discount_compute = fields.Float(string="Tổng tiền giảm giá",
                                    compute='compute_discount',
                                    compute_sudo=True, store=True)

    count_inventory_fees_invoice = fields.Integer(string="Hóa đơn phí lưu kho", compute="compute_count_inventory_fees_invoice")

    def compute_count_inventory_fees_invoice(self):
        for rec in self:
            rec.count_inventory_fees_invoice = 0
            invoices = self.env['account.move'].sudo().search(
                [('sale_order_id', '=', rec.id), ('is_inventory_fees', '=', True)])
            rec.count_inventory_fees_invoice = len(invoices)

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

    ### TODO gui tin nhan
    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     template = self.env.ref('advanced_invoice.mail_template_data_sale_order_confirm', raise_if_not_found=False)
    #     for order in self:
    #         if template:
    #             template.send_mail(order.id, force_send=True, raise_exception=False)
    #         if order.x_studio_mobile:
    #             phone = str(order.x_studio_mobile)
    #             bid = order.name
    #             sms = "Cam on quy khach da dat hang tai SOFACOMPANY. Ma don hang [" + order.name + "] tri gia [" + order.get_format_amount_total() + "]d. CSKH: 1900636845 (10:00 - 18:00)"
    #             url = "https://cloudsms4.vietguys.biz:4438/api/index.php?u=sofacompany&pwd=28ruv&from=SOFACOMPANY&phone=%s&sms=%s&bid=%s&type=8&json=1" % (
    #             phone, sms, bid)
    #             payload = {}
    #             headers = {}
    #             try:
    #                 res = requests.request("POST", url, headers=headers, data=payload)
    #                 print(res.json())
    #             except:
    #                 e = 0
    #     return res
    ### TODO gui tin nhan

    def action_open_inventory_fees_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id), ('is_inventory_fees', '=', True)]
        action['context'] = {'create': False, 'edit': True}
        return action
