# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class MrpProductionCustom(models.Model):
    _inherit = 'mrp.production'
    
    def action_confirm(self):
        for w in self.workorder_ids:
            if self.product_qty > w.workcenter_id.default_capacity:
                raise UserError(f"No puede confirmar una orden por una cantidad ({self.product_qty}) superior al Centro de Trabajo {w.workcenter_id.name} ({w.workcenter_id.default_capacity})")

        for w in self.workorder_ids:
            if w.workcenter_id.working_state != 'normal':
                lines = []

                for l in self.workorder_ids:
                    lines.append({
                        'name': l.name,
                        'workcenter_id': l.workcenter_id.id,
                        'workorder_id':l.id,
                        'working_state': l.working_state
                        })

                action = self.env['ir.actions.act_window']._for_xml_id('mrp_custom.change_workcenter_action')
                action['view_mode'] = 'form'
                action['views'] = [(False, 'form')]
                action['target'] = 'new'
                action['context'] = {
                    'default_mrp_production_id': self.ids,
                    'default_change_workcenter_line_ids': lines
                }
                return action

        super(MrpProductionCustom, self).action_confirm()

    def action_dispach_by_product(self):
        self.ensure_one()
        return {
            'name': _('Despachar Subproductos'),
            'view_mode': 'form',
            'res_model': 'dispatch.by.product',
            'views': [[self.env.ref('mrp_custom.dispatch_by_product_wizard_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'context': {},
            'target': 'new',
        }