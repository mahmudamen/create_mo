from odoo import fields, models, api, _


class product(models.Model):
    _inherit = 'product.product'
    _description = 'Description'

    product_name = fields.Char(string='name',related="product_tmpl_id.name")






    def action_create_mrp(self):
        return False