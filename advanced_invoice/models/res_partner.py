from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # contact_address_full = fields.Char()

    # @api.depends('street', 'street2', 'state_id', 'x_ward_id', 'x_district_id', 'country_id')
    # def _compute_complete_full(self):
    #     for record in self:
    #         record.contact_address_full = ''
    #         x= ''
    #         if record.street:
    #             x += record.street + ', '
    #         if record.street2:
    #             x += record.street2 + ', '
    #         if record.x_ward_id:
    #             x += record.x_ward_id.x_name + ', '
    #         if record.x_district_id:
    #             x += record.x_district_id.x_name + ', '
    #         if record.state_id:
    #             x += record.state_id.name + ', '
    #         if record.country_id:
    #             x += record.country_id.name
    #         record.contact_address_full = x[0:-2]