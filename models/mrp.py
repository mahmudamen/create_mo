# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY info@odoo-experte.com <https://www.odoo-experte.com>
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order',
                                    string='Sale Order')
    sale_order_line_id = fields.Many2one('sale.order.line',
                                         string="Sale Order Line")
    all_number = fields.Integer(string='All Number')
    number = fields.Integer(string='Number')


    def unlink(self):
        for mrp in self:
            if mrp.sale_order_line_id:
                mrp.sale_order_line_id.mrp_id = False
                mrp.sale_order_line_id.need_mrp = False
        return super(MrpProduction, self).unlink()


    def write(self, values):
        for mrp in self:
            if values.get('state') == 'cancel':
                mrp.sale_order_line_id.write({'mrp_id': None,
                                              'need_mrp': False})
        return super(MrpProduction, self).write(values)
