
from datetime import datetime, timedelta


from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

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
                else:
                    raise UserError(_('can not find bom'))

class MoWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    def record_production(self):
        if not self:
            return True

        self.ensure_one()
        self._check_company()
        if float_compare(self.qty_producing, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

        # Ensure serial numbers are used once
        if self.product_id.tracking == 'serial' and self.finished_lot_id:
            line = self.finished_workorder_line_ids.filtered(
                lambda line: line.lot_id.id == self.finished_lot_id.id
            )
            if line:
                raise UserError(_('You cannot produce the same serial number twice.'))

        # If last work order, then post lots used
        if not self.next_work_order_id:
            self._update_finished_move()

        # Transfer quantities from temporary to final move line or make them final
        self._update_moves()

        # Transfer lot (if present) and quantity produced to a finished workorder line
        if self.product_tracking != 'none':
            self._create_or_update_finished_line()

        # Update workorder quantity produced
        #self.qty_produced += self.qty_producing

        # Suggest a finished lot on the next workorder
        if self.next_work_order_id and self.product_tracking != 'none' and (not self.next_work_order_id.finished_lot_id or self.next_work_order_id.finished_lot_id == self.finished_lot_id):
            self.next_work_order_id._defaults_from_finished_workorder_line(self.finished_workorder_line_ids)
            # As we may have changed the quantity to produce on the next workorder,
            # make sure to update its wokorder lines
            self.next_work_order_id._apply_update_workorder_lines()

        # One a piece is produced, you can launch the next work order
        self._start_nextworkorder()

        # Test if the production is done
        rounding = self.production_id.product_uom_id.rounding
        production_qty = self._get_real_uom_qty(self.qty_production)
        if float_compare(self.qty_produced, production_qty, precision_rounding=rounding) < 0:
            previous_wo = self.env['mrp.workorder']
            if self.product_tracking != 'none':
                previous_wo = self.env['mrp.workorder'].search([
                    ('next_work_order_id', '=', self.id)
                ])
            candidate_found_in_previous_wo = False
            if previous_wo:
                candidate_found_in_previous_wo = self._defaults_from_finished_workorder_line(previous_wo.finished_workorder_line_ids)
            if not candidate_found_in_previous_wo:
                # self is the first workorder
                self.qty_producing = self.qty_remaining
                self.finished_lot_id = False
                if self.product_tracking == 'serial':
                    self.qty_producing = 1

            self._apply_update_workorder_lines()
        else:
            self.qty_producing = 0
            self.button_finish()
        return True