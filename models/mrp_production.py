# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, tools, _
from odoo.osv import expression
from odoo.exceptions import UserError





class MrpProductionCustom(models.Model):
    _inherit = 'mrp.production'

    lote = fields.Char(string='Lote', readonly=True, copy=False)
    process_id = fields.Many2one('manufacturing.processes', 
                                 string='Proceso', 
                                 copy=False,
                                 default= lambda self: self.env.ref('mrp_custom.manufacturing_process_1').id)
    process_name = fields.Char(string='Proceso', compute="_compute_process_name", readonly=True, copy=False)

    

    @api.depends('process_id')
    def _compute_process_name(self):
        for record in self:
            record.process_name = record.process_id.get_selection_label('process', record.process_id.process)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=1, order=None):
        domain = domain or []
        name_domain = [('name', 'ilike', name),('lote', 'ilike', name)]
        domain = expression.AND([name_domain, domain])
        return self._search(domain, limit=limit, order="id  desc")
    
  
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} - lote: {record.lote if record.lote else ''}"

    

    def action_switch_work_center(self):
        self.ensure_one()

        return {
            'name': _('Cambiar Centro de Trabajo'),
            'view_mode': 'form',
            'res_model': 'switch.workcenter',
            'views': [[self.env.ref('mrp_custom.switch_workcenter_wizard_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'context': {'default_product_id': self.product_id.id},
            'target': 'new',
        }
    
    
    def action_confirm(self):
        # Esta funcionalidad va a ser cambiada por el nuevo wizard que estoy construyendo
        # import ipdb; ipdb.set_trace()
        for w in self.workorder_ids:
            if self.product_qty > w.workcenter_id.default_capacity:
                return self.action_switch_work_center()

        # asignar el lote
        self.lote = self.env['ir.sequence'].next_by_code('mrp.custom')
        super(MrpProductionCustom, self).action_confirm()

    def action_dispach_by_product(self):
        self.ensure_one()
        return {
            'name': _('Despachar Subproducto'),
            'view_mode': 'form',
            'res_model': 'dispatch.by.product',
            'views': [[self.env.ref('mrp_custom.dispatch_by_product_wizard_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'context': {},
            'target': 'new',
        }
    
    def action_send_to_other_locations(self):
        self.ensure_one()
        return {
            'name': _('Enviar a Otra Ubicación'),
            'view_mode': 'form',
            'res_model': 'merge.om',
            'views': [[self.env.ref('mrp_custom.view_merge_om_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'context': {},
            'target': 'new',
        }



    def _prepate_next_process(self, product, process):
        bom_id = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id), 
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)], 
            limit=1)
        
        return {
                    'product_id': product.id,
                    'product_qty': self.product_qty,
                    'bom_id': bom_id.id,
                    'process_id': process.id,
                }
    
    def action_send_to_process_two(self):
        self.ensure_one()
        # import pdb; pdb.set_trace()
        MO = self.env['mrp.production']
        mo = False

        # process 1 is setting by default
        if self.process_id.process == 'process_1':
            process = self.env.ref('mrp_custom.manufacturing_process_2')
            mo = MO.create(self._prepate_next_process(self.process_id.product_id, process))
            
        # process 2 
        if self.process_id.process == 'process_2':
           process = self.env.ref('mrp_custom.manufacturing_process_3')
           mo = MO.create(self._prepate_next_process(self.process_id.product_id, process))

        # process 3
        if self.process_id.process == 'process_3':
            process = self.env.ref('mrp_custom.manufacturing_process_4')
            mo = MO.create(self._prepate_next_process(self.process_id.product_id, process))

        # process 4
        if self.process_id.process == 'process_4':
            process = self.env.ref('mrp_custom.manufacturing_process_5')
            mo = MO.create(self._prepate_next_process(self.process_id.product_id, process))

        return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': mo.id,
            }
