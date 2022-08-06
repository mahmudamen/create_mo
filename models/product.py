
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class product(models.Model):
    _inherit = 'product.product'
    _description = 'Description'

    product_name = fields.Char(string='name',related="product_tmpl_id.name")
    product_source = fields.Char(string='Cut number')
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
        last_id = self.env['mrp.routing'].search([])[-1].id
        for i in self:
            if i.product_qty <= 0:
                raise UserError(_('qty cant be zero' ))
            else:
                mrp_bom = self.env['mrp.bom'].search([('product_tmpl_id','=',i.product_tmpl_id.id)])

                if mrp_bom:
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
                    s = self.env['mrp.production'].create(production_vals)
                    o = self.env['mrp.production'].search([('id','=',s.id)])
                    m = o._onchange_move_raw()
                    a = o.action_confirm()
                else:
                    raise UserError(_('can not find bom'))



class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'


    previous_order_qty = fields.Float(string='Previous Order Qty', default=0.0,
                                          compute='_compute_previous_order_qty')

    def _compute_previous_order_qty(self):
        for rec in self:
            last_step_qty = 0.0
            previous_wo = self.env['mrp.workorder'].search([ ('next_work_order_id', '=', rec.id)])
            last_step_qty = previous_wo.qty_produced
            rec.previous_order_qty = last_step_qty