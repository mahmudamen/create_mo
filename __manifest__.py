# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY info@odoo-experte.com <https://www.odoo-experte.com>
# See LICENSE file for full copyright and licensing details.

{
    "name": "create mo",
    "summary": "",
    "version": '11.0.1.2.0',
    "category": 'Extra Tools',
    'license': 'OPL-1',
    'support': 'info@odoo-experte.com',
    'author': "Odoo-experte",
    'website': "https://www.odoo-experte.com",
    'depends': [
        'sale',
        'mrp',
        'account',
    ],
    'data': [
        'wizard/create_mrp_wizard_views.xml',
        'views/sale_views.xml',
        'views/product.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    "application": False,
    'installable': True,
    'auto_install': False,
}
