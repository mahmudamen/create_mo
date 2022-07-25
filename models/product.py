from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta

class product(models.Model):
    _inherit = 'product.product'
    _description = 'Description'

    product_name = fields.Char(string='name',related="product_tmpl_id.name")
    product_source = fields.Char()
    product_qty = fields.Float(string='Quantity',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'))

    def action_bom_cost(self):

        view_id_form = self.env['ir.ui.view'].search([('name', '=', 'create_mrp_wizard_form')])
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', 'create_mrp_wizard_form')])


        return {
            'type': 'ir.actions.act_window',
            # 'name': _('Product'),
            'res_model': 'create.mrp.wizard',
            'view_type': 'form',
            'view_mode': 'tree,form',
            # 'view_id': view_id_tree.id,
            'views': [(view_id_tree.id, 'tree'), (view_id_form.id, 'form')],
            'target': 'current',
            # 'res_id': your.model.id,
        }


    def action_create_mrp(self):

        for i in self:
            bom_values = {
                    'product_tmpl_id':
                        i.id,
                    'product_id':
                         i.id,
                    'type': 'normal',
                    'product_qty': 1,
                }
            mrp_bom = self.env['mrp.bom'].create(bom_values)
            production_vals = {
                    'product_id': i.id,
                    'bom_id': mrp_bom.id,
                    'product_qty': i.product_qty,
                    'date_planned_start': datetime.now() + timedelta(days=14),
                    'date_planned_finished': datetime.now() + timedelta(days=24),
                    'product_uom_id':i.uom_id.id,
                    # 'purchase_order_line_id': purchase_order_line_id,
                    'origin':i.product_source,
                    'all_number': 1,
                    'number': 1,
                    # 'spec_url': line.spec_url,
                    # 'attachment_id': line.attachment_id.id,
                }
            self.env['mrp.production'].create(production_vals)


