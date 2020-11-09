import json

from odoo import http
from odoo.http import request


class SofavnNewsletter(http.Controller):

    @http.route('/sofavn/subscribe/', auth='public', type='json', csrf=False)
    def sofavn_subscribe_newsletter(self, **kw):
        if 'email' in kw:
            email = kw['email']
            if len(email) > 0:
                try:
                    partner = request.env['res.partner'].sudo().search([("email", "=", email)], limit=1)
                    if len(partner) > 0:
                        partner.sudo().is_subcribe_newsletter = True
                    else:
                            request.env['res.partner'].with_context(mail_create_nosubscribe=True).sudo().create({
                                'email': email,
                                'name': email,
                                'is_subscribe_newsletter': True,
                            })
                    return {'success': True, 'message': 'Success'}
                except Exception as ex:
                    print(ex)
                    return {'success': False, 'message': 'Create contact failed'}
            else:
                return {'success': False, 'message': 'Email is empty'}
        else:
            return {'success': False, 'message': 'Email is empty'}


        # data = request.env['ProjectName.TableName'].sudo().search([("id", "=", int(Var))])

        # if data:
        #     values['success'] = True
        #     values['return'] = "Something"
        # else:
        #     values['success'] = False
        #     values['error_code'] = 1
        #     values['error_data'] = 'No data found!'
        #
        # return json.dumps(values)
