# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError

class SwitchWorkCenter(models.TransientModel):
    _name = 'switch.workcenter'
    _description = 'Switch Workcenter'


    workcenter_ids = fields.One2many(
        'switch.workcenter.line', 
        'switch_workcenter_id', 
        'Work Centers'
        )
    
    product_id = fields.Many2one('product.product', string='Producto', help="Technical field used to compute the capacity")

    @api.constrains('workcenter_ids')
    def _check_totals(self):
        cap_used_total = 0
        cap_total = 0
        for line in self.workcenter_ids:
            if line.select:
                cap_used_total += line.capacity_used
                cap_total += line.capacity
        if cap_used_total > cap_total:
            raise ValidationError(_('El total de la capacidad a ocupar superar el total de la capacidad de los centros de trabajo seleccionados'))

    def update_workcenter(self, mo_record, line):
        """ Update the workcenter of the Operations."""
        for wc in mo_record.workorder_ids:
            wc.write({
                    'workcenter_id': line.workcenter_id.id,
                })

    def update_product_qty_origin(self):
        active_id = self._context.get('active_id')
        MO = self.env['mrp.production'].browse(active_id)
        cap_used_total = 0
        for line in self.workcenter_ids:
            if line.select:
                cap_used_total += line.capacity_used
        result = cap_used_total - MO.product_qty
        MO.write({'product_qty': abs(result)})

    def post_message(self, mo_record):
        active_id = self._context.get('active_id')
        MO = self.env['mrp.production'].browse(active_id)
        message_body = f"""Se ha creado la orden de manufactura {mo_record.name} para producir {mo_record.product_qty}  
        unidades de {mo_record.product_id.name}"""
        MO.message_post(
                body=message_body
            )

    def action_switch_workcenter(self):
        self.ensure_one()
        MO = self.env['mrp.production']
        bom_id = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id), 
            ('company_id', '=', self.env.company.id),
            ('active', '=', True)], 
            limit=1)
        if not bom_id:
            raise UserError(_(f'No se encontro una lista de Materiales para el producto {self.product_id.name}'))
        for line in self.workcenter_ids:
            if line.select:
                mo_record = MO.create({
                    'product_id': self.product_id.id,
                    'product_qty': line.capacity_used,
                    'workcenter_id': line.workcenter_id.id,
                    'bom_id': bom_id.id,
                    'lote':line.lote,
                })

                self.update_workcenter(mo_record, line)
                self.post_message(mo_record)

        # Update quantity in OM original
        self.update_product_qty_origin()
        
        


class SwitchWorkcenterLine(models.TransientModel):
    _name = 'switch.workcenter.line'
    _description = 'Switch Workcenter Line'

    switch_workcenter_id = fields.Many2one('switch.workcenter', 'Switch Work Center')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Centro de Trabajo', domain=[('active', '=', True),('working_state', '=', 'normal')])
    capacity_used = fields.Float('Capacidad a ocupar')
    capacity = fields.Float('Capacidad Max.')
    lote = fields.Char('Lote')
    select = fields.Boolean('Seleccionar', default=False)

    @api.onchange('select')
    def _onchange_select(self):
        for line in self:
            if line.select and not line.lote:
                self.lote = self.env['ir.sequence'].next_by_code('mrp.custom')


    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        for line in self:
            if line.workcenter_id:
                line.capacity = line.workcenter_id.default_capacity


    @api.constrains('capacity_used', 'capacity', 'select')
    def _check_capacity(self):
        active_id = self._context.get('active_id')
        MO = self.env['mrp.production'].browse(active_id)
        for line in self:
            if line.select:
                if line.capacity_used > line.capacity:
                    raise ValidationError(_('La cantidad indicada es mayor a la capacidad del centro de trabajo'))
                if line.capacity_used < 0:
                    raise ValidationError(_('La cantidad no puede ser negativa'))
                if line.capacity_used == 0:
                    raise ValidationError(_('La cantidad no puede ser 0'))
                if line.capacity_used > MO.product_qty:
                    raise ValidationError((f'La cantidad producida es mayor a la de la orden de manufactura {MO.name}'))
                    
            if not line.select:
                raise ValidationError(_('Debe seleccionar una ubicación antes de aceptar.'))
            