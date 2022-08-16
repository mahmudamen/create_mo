from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class product(models.Model):
    _inherit = 'product.product'
    _description = 'Description'

    product_name = fields.Char(string='name', related="product_tmpl_id.name")
    product_source = fields.Char(string='Cut number')
    product_qty = fields.Float(string='Quantity',
                               digits=dp.get_precision(
                                   'Product Unit of Measure'))

    def action_create_mrp(self):
        last_id = self.env['mrp.routing'].search([])[-1].id
        for i in self:
            if i.product_qty <= 0:
                raise UserError(_('qty cant be zero'))
            else:
                mrp_bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', i.product_tmpl_id.id)])

                if mrp_bom:
                    z = self.env['ir.sequence'].next_by_code('mrp.production')
                    production_vals = {
                        'name':z,
                        'product_id': i.id,
                        'bom_id': mrp_bom.id,
                        'product_qty': i.product_qty,
                        'date_planned_start': datetime.now() + timedelta(days=14),
                        'date_planned_finished': datetime.now() + timedelta(days=24),
                        'product_uom_id': i.uom_id.id,
                        'picking_type_id':8,
                        # 'purchase_order_line_id': purchase_order_line_id,
                        'origin': i.product_source,
                        'all_number': 1,
                        'number': 1,
                        
                        'group_id': self.procurement_group_id.id,
                        'propagate_cancel': self.propagate_cancel,
                    }

                    s = self.env['mrp.production'].create(production_vals)
                    o = self.env['mrp.production'].search([('id', '=', s.id)])
                    x = self.env['stock.picking'].search([('id', '=', o.picking_ids.ids)])
                    for i in x:
                        x.origin = o.origin
                    m = s._onchange_move_raw()
                    a = s.action_confirm()
                else:
                    raise UserError(_('can not find bom'))


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    previous_order_qty = fields.Float(string='Previous Order Qty', default=0.0,
                                      compute='_compute_previous_order_qty')
    origin = fields.Char('cut numer')

    def _compute_previous_order_qty(self):
        for rec in self:
            last_step_qty = 0.0
            previous_wo = self.env['mrp.workorder'].search([('next_work_order_id', '=', rec.id)])
            last_step_qty = previous_wo.qty_produced
            rec.previous_order_qty = last_step_qty




class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    def button_plan(self):
        res = super(MrpProduction, self).button_plan()

        for i in self.workorder_ids:
            i.origin = self.origin

        return res

    def _get_finished_move_value(self, product_id, product_uom_qty, product_uom, operation_id=False,
                                 byproduct_id=False):
        return {
            'product_id': product_id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom,
            'operation_id': operation_id,
            'byproduct_id': byproduct_id,
            'unit_factor': product_uom_qty / self.product_qty,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_finished,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.product_id.with_context(force_company=self.company_id.id).property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.location_dest_id.get_warehouse().id,
            'origin': self.origin,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids if not byproduct_id],
        }

    def _get_move_raw_values(self, bom_line, line_data):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        source_location = self.location_src_id
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'reference': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.with_context(
                force_company=self.company_id.id).property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.origin,
            'state': 'draft',
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
        }
        return data


    def action_confirm(self):
        action_confirm = super(MrpProduction, self).action_confirm()
        return action_confirm
