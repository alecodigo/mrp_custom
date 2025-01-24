# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    mrp_localtion_dest_id = fields.Many2one('stock.location', string="Ubicación Destino para la merma")
    mrp_localtion_dest_prod_finished_id = fields.Many2one('stock.location', string="Ubicación Destino para el subproducto terminado")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        mrp_localtion_dest = self.env['ir.config_parameter'].sudo().get_param('mrp_custom.mrp_localtion_dest_id')
        mrp_localtion_dest_prod_finished_id = self.env['ir.config_parameter'].sudo().get_param('mrp_custom.mrp_localtion_dest_prod_finished_id')
        res.update(
            mrp_localtion_dest_id=int(mrp_localtion_dest) if mrp_localtion_dest else False,
            mrp_localtion_dest_prod_finished_id=int(mrp_localtion_dest_prod_finished_id) if mrp_localtion_dest_prod_finished_id else False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('mrp_custom.mrp_localtion_dest_id', self.mrp_localtion_dest_id.id if self.mrp_localtion_dest_id else False)
        self.env['ir.config_parameter'].sudo().set_param('mrp_custom.mrp_localtion_dest_prod_finished_id', self.mrp_localtion_dest_prod_finished_id.id if self.mrp_localtion_dest_prod_finished_id else False)
    

