# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.template'

    by_product = fields.Boolean(string='Subproducto', default=False)

    @api.onchange('by_product')
    def _onchange_by_product(self):
        if self.by_product:
            self.product_variant_id.by_product = True
        else:
            self.product_variant_id.by_product = False
            

class ProductProduct(models.Model):
    _inherit = 'product.product'

    by_product = fields.Boolean(string='Subproducto', default=False)