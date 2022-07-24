# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY info@odoo-experte.com <https://www.odoo-experte.com>
# See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta


class CreateMrpWizard(models.TransientModel):
    _name = 'create.mrp.wizard'

    order_line_ids = fields.One2many('create.mrp.line.wizard',
                                     'order_wizard_id',
                                     string='Products')

    @api.model
    def default_get(self, fields_list):
        res = super(CreateMrpWizard, self).default_get(fields_list)
        if fields_list:
            order_line_obj = self.env['product.product'].search([('id','!=',0)])
            lines = []
            line_wizard_pool = self.env['create.mrp.line.wizard']
            for line in order_line_obj:
                line_wizard = line_wizard_pool. \
                    create({'product_tmpl_id':line.id})
                lines.append(line_wizard.id)
            res.update({'order_line_ids': [(6, 0, lines)]})
        return res



    def action_create_mrp(self):
        for i in self.order_line_ids:
            if i.checkbox:
                bom_values = {
                    'product_tmpl_id':
                        469,
                    'product_id':
                         i.product_id.id,
                    'type': 'normal',
                    'product_qty': i.product_qty,
                }
                mrp_bom = self.env['mrp.bom'].create(bom_values)
                production_vals = {
                    'product_id': i.product_tmpl_id.id,
                    'bom_id': mrp_bom.id,
                    'product_qty': i.product_qty,
                    'date_planned_start': datetime.now() + timedelta(days=14),
                    'date_planned_finished': datetime.now() + timedelta(days=24),
                    'product_uom_id':1,
                    # 'purchase_order_line_id': purchase_order_line_id,
                    'origin': i.product_source,
                    'all_number': 1,
                    'number': 1,
                    # 'spec_url': line.spec_url,
                    # 'attachment_id': line.attachment_id.id,
                }
                self.env['mrp.production'].create(production_vals)





class CreateMrpLineWizard(models.TransientModel):
    _name = 'create.mrp.line.wizard'

    order_wizard_id = fields.Many2one('create.mrp.wizard',
                                      string='Purchase Order',
                                      ondelete='cascade', )
    order_line_ids = fields.One2many('create.mrp.line.wizard.line',
                                     'order_wizard_id',
                                     string='Products')
    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.template', string='Product')
    product_tmpl_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'))
    checkbox = fields.Boolean(' ')
    product_source = fields.Char()



class CreateMrpLineWizardLine(models.TransientModel):
    _name = 'create.mrp.line.wizard.line'

    order_wizard_id = fields.Many2one('create.mrp.line.wizard',
                                      string='Purchase Order',
                                      ondelete='cascade', )
    name = fields.Text(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'))

class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
