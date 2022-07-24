# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY info@odoo-experte.com <https://www.odoo-experte.com>
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mrp_ids = fields.One2many('mrp.production',
                              'sale_order_id',
                              string="Manufacturing Order",
                              copy=False)


    def action_cancel(self):
        for sale in self:
            for mrp in sale.mrp_ids:
                if mrp.state not in ('draft', 'cancel', 'done'):
                    raise ValidationError(
                        _('Sie können die Bestellung nicht Stornieren, '
                          'Sie müssen alle zugehörige Fertigungsaufträge '
                          'Stornieren. '))
                mrp.action_cancel()
        return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    need_mrp = fields.Boolean(string="MRP", default=False,
                              help='Need Manufacturing')
    mrp_id = fields.Many2one('mrp.production',
                             string="Manufacturing Order",
                             copy=False)
