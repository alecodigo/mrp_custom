# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ManufacturingProcesses(models.Model):
    _name = 'manufacturing.processes'
    _description = 'Manufacturing Processes'

    name = fields.Char('Descripción')
    product_id = fields.Many2one('product.product', 'Producto')
    process = fields.Selection([
        ('process_1', 'Proceso 1'), 
        ('process_2', 'Proceso 2'), 
        ('process_3', 'Proceso 3'),
        ('process_4', 'Proceso 4'),
        ('process_5', 'Proceso 5'),
        ], string='Proceso')


    @api.constrains('product_id')
    def _check_product_id(self):
        """Check if the product have a bom."""
        bom_id = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id), 
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)], 
            limit=1)
        if bom_id.product_tmpl_id != self.product_id.product_tmpl_id:
            raise ValidationError(_("El producto debe tener una lista de materiales."))
        
    @api.model
    def get_selection_label(self, field_name, value):
        """Devuelve la etiqueta visible de un campo selection."""
        field_info = self.fields_get([field_name])
        selection = field_info[field_name].get('selection', [])
        label = dict(selection).get(value, 'Valor no encontrado')
        return label