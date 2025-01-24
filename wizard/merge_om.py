# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MergeOM(models.TransientModel):
    _name = "merge.om"

    workcenter_ids = fields.One2many(
        'merge.om.line',
        'merge_om_id',
        'Work Centers'
        )

    def action_confirm(self):
        self.ensure_one()

        def workcenter_ids():
            return [(4, i.id) for i in self.workcenter_ids]        
        
        if len(self.workcenter_ids) > 1:
            return {
                'name': _('Unir lotes'),
                'view_mode': 'form',
                'res_model': 'merge.om',
                'views': [[self.env.ref('mrp_custom.view_merge_om_step2_form').id, 'form']],
                'type': 'ir.actions.act_window',
                'context': {'default_workcenter_ids': workcenter_ids()},
                'target': 'new',
            }
        else:
            raise UserError(_("Debe seleccionar al menos dos centro de trabajo"))


    def merge_mro(self):
        lines = self.workcenter_ids.filtered(lambda line: line.select == True)
        if len(lines) > 1:
            raise UserError(_("Debe seleccionar solamente un número de lote."))
        mro = self.workcenter_ids.mapped('operation_num_id')
        mro.action_merge()
        

class MergeOMLine(models.TransientModel):
    _name = "merge.om.line"


    operation_num_id = fields.Many2one('mrp.production', 'Lote', domain=[('state', 'in', ('draft', 'done'))])
    operation = fields.Char('Número de Operación')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Centro de Trabajo', domain=[('active', '=', True),('working_state', '=', 'normal')])
    merge_om_id = fields.Many2one('merge.om', 'Merge OM')
    demand_forecast = fields.Float('Demanda')
    order_qty = fields.Float('Cantidad de Orden')
    capacity = fields.Float('Capacidad Max.')
    select = fields.Boolean('Seleccionar', default=False)

    @api.onchange('operation_num_id')
    def _onchange_operation_num_id(self):
        for line in self:
            line.operation = line.operation_num_id.name
            line.order_qty = line.operation_num_id.product_qty
            try:
                if line.operation_num_id:
                    result = line.operation_num_id.workorder_ids.mapped('workcenter_id')
                    if len(result) >= 1:
                        line.workcenter_id = result[0].id
                    
            except Exception as e:
                raise UserError(e)

    
    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        for line in self:
            if line.workcenter_id:
                line.capacity = line.workcenter_id.default_capacity
