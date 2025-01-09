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
        self.ensure_one()
        stock_move_obj = self.env['stock.move']
        for record in self:
            stock_move = stock_move_obj.create({
                'name': record.product_id.name,
                'product_id': record.product_id.id,
                'product_uom_qty': record.quantity,
                'product_uom': record.product_id.uom_id.id,
                'location_id': record.location_id.id,
                'location_dest_id': record.location_dest_id.id,
            })
            stock_move._action_confirm()
            stock_move._action_assign()
            stock_move._action_done()
        return True