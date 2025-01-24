# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import logging
_logger = logging.getLogger(__name__)


class DispatchByProduct(models.TransientModel):
    _name = 'dispatch.by.product'
    _description = 'Wizard for Inventory Transfer'


    def _default_mrp_id(self):
        if self._context.get('default_mrp_id'):
            return self._context.get('default_mrp_id')
        
    def _default_location_dest_id(self):
        location_dest_id = self.env['ir.config_parameter'].sudo().get_param('mrp_custom.mrp_localtion_dest_id')
        if location_dest_id and location_dest_id.isdigit():
            return int(location_dest_id)

    product_id = fields.Many2one('product.product', string='Producto', domain=[('by_product', '=', True)], required=True)
    quantity = fields.Float(string='Cantidad', required=True, default=1.0)
    location_id = fields.Many2one('stock.location', string='Ubicación de Origen', required=True)
    location_dest_id = fields.Many2one('stock.location', string='Ubicación de Destino', required=True, default=_default_location_dest_id)
    date_done = fields.Date(string='Fecha de Efectiva', required=True)
    mrp_id = fields.Many2one('mrp.production', string='Orden de Fabricación', default=_default_mrp_id)


    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity >  record.mrp_id.product_qty:
                raise ValidationError(_('Cantidad de producto superior a la cantidad disponible'))

    def _picking_out_product(self, bom):
        def _compute_qty_product():
            for record in self:
                result = record.mrp_id.product_qty - record.quantity
                if result == 0:
                    raise ValidationError(_('Cantidad de producto debe ser igual o superior a 1.'))
                return result
            
        group_id = bom.procurement_group_id.id
        location_dest_product_id = self.env['ir.config_parameter'].sudo().get_param('mrp_custom.mrp_localtion_dest_prod_finished_id')
        if location_dest_product_id and location_dest_product_id.isdigit():
            location_dest_product_id = int(location_dest_product_id)
        for record in self:
            self.env['stock.picking.type'].search([('code', '=', 'mrp_operation')], limit=1).id
            # picking out
            picking ={
                'origin': bom.name,
                'partner_id': self.env.user.partner_id.id,
                'picking_type_id': self.env.ref('stock.picking_type_out').id,  # Tipo de picking
                'location_id': record.location_id.id, # Origin
                'location_dest_id': location_dest_product_id, # Final Destination
                'date_done': record.date_done,
                'group_id': group_id,
                'move_ids_without_package': [(0, 0, {
                    'name': record.mrp_id.product_id.name,
                    'product_id': record.mrp_id.product_id.id,
                    'product_uom_qty': _compute_qty_product(),
                    'product_uom': record.product_id.uom_id.id,
                    'location_id': bom.location_dest_id.id, # Origin
                    'location_dest_id': location_dest_product_id, # Final Destination
                    'group_id': group_id,
                })]
            }
        return picking

    def _picking_in_subproduct(self, bom):
        group_id =  bom.procurement_group_id.id
        for record in self:
            # picking in
            picking = {
                'origin': bom.name,
                'partner_id': self.env.user.partner_id.id,
                'picking_type_id': self.env.ref('stock.picking_type_in').id,  # Tipo de picking
                'location_id': record.location_id.id,
                'location_dest_id': record.location_dest_id.id,
                'date_done': record.date_done,
                'group_id': group_id,
                'move_ids_without_package': [(0, 0, {
                    'name': record.product_id.name,
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.quantity,
                    'product_uom': record.product_id.uom_id.id,
                    'location_id': record.location_id.id,
                    'location_dest_id': record.location_dest_id.id,
                    'group_id': group_id,
                })]
            }
        return picking

    def action_transfer_by_product(self):
        self.ensure_one()        
        stock_picking = self.env['stock.picking']
        active_id = self._context.get('active_id')
        bom = self.env['mrp.production'].browse([active_id])
        # picking out
        picking_out_product = stock_picking.create(self._picking_out_product(bom))
        _logger.info("Picking de Salida producto terminado creado %s" % picking_out_product.name)
        # picking in
        picking_in_subproduct = stock_picking.create(self._picking_in_subproduct(bom))
        _logger.info("Picking de entrada merma creado %s" % picking_in_subproduct.name)
        return True