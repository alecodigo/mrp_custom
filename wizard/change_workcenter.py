# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class ChangeWorkcenter(models.TransientModel):
    _name = 'change.workcenter'
    _description = 'Change Workcenter'

    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center')
    individual = fields.Boolean('Actualización individual', default=True)
    mrp_production_id = fields.Many2one('mrp.production', 'Orden de Fabricación')
    change_workcenter_line_ids = fields.One2many('change.workcenter.line', 'change_workcenter_id', 'Lines')

    def update_change(self):
        for c in self.change_workcenter_line_ids:
            if self.individual:
                c.workorder_id.workcenter_id = c.workcenter_id.id
            else:
                c.workorder_id.workcenter_id = self.workcenter_id.id

        self.mrp_production_id.action_confirm()

class ChangeWorkcenterLine(models.TransientModel):
    _name = 'change.workcenter.line'
    _description = 'Change Workcenter Line'

    change_workcenter_id = fields.Many2one('change.workcenter', 'Change Work Center')
    name = fields.Char('Orden de trabajo')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Centro de trabajo')
    workorder_id = fields.Many2one('mrp.workorder', 'Orden de trabajo')
    working_state = fields.Selection(related='workcenter_id.working_state')
