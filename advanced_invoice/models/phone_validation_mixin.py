from odoo import fields, models, api


class PhoneValidationMixin(models.AbstractModel):
    _inherit = 'phone.validation.mixin'

    def _phone_get_country(self):
        return False