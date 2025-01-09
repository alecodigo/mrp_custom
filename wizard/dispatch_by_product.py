# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta


class DispatchByProduct(models.TransientModel):
    _name = 'dispatch.by.product'
    _description = 'Wizard for Inventory Transfer'

    product_id = fields.Many2one('product.product', string='Product', domain=[('by_product', '=', True)], required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    location_id = fields.Many2one('stock.location', string='Source Location', required=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', required=True)

    def action_transfer_by_product(self):
        # import ipdb; ipdb.set_trace()
        stock_picking = self.env['stock.picking']
        self.ensure_one()
        for wizard in self:
            picking = stock_picking.create({
                'partner_id': self.env.user.partner_id.id,
                'picking_type_id': self.env.ref('stock.picking_type_internal').id,  # Tipo de picking
                'location_id': wizard.location_id.id,
                'location_dest_id': wizard.location_dest_id.id,
                'move_ids_without_package': [(0, 0, {
                    'name': wizard.product_id.name,
                    'product_id': wizard.product_id.id,
                    'product_uom_qty': wizard.quantity,
                    'product_uom': wizard.product_id.uom_id.id,
                    'location_id': wizard.location_id.id,
                    'location_dest_id': wizard.location_dest_id.id,
                })]
            })
            picking.button_validate()
        return True