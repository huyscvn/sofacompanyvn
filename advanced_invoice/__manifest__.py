# -*- coding: utf-8 -*-
{
    'name': "advanced_invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'sale_stock', 'sale_coupon', 'stock', 'phone_validation', 'contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/templates.xml',
        'views/quotation_template.xml',
        'views/sale_order_views.xml',
        'views/invoice_template.xml',
        'views/account_move_views.xml',
        'views/product_template_views.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode

}
