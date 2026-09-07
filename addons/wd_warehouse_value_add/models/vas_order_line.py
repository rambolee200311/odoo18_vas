# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VasOrderLine(models.Model):
    _name = 'wd.vas.order.line'
    _description = 'Warehouse VAS Order Line'
    _order = 'sequence, id'

    order_id = fields.Many2one(
        'wd.vas.order',
        string='VAS Order',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    operation_type_id = fields.Many2one(
        'wd.vas.operation.type',
        string='Operation Type',
        required=True,
        ondelete='restrict',
    )
    quantity_time = fields.Float(
        string='Quantity / Time',
        digits=(16, 4),
    )
    unit_id = fields.Many2one(
        'world.depot.charge.unit',
        string='Unit',
        required=True,
        readonly=True,
        ondelete='restrict',
    )
    note = fields.Text(string='Note')

    @api.onchange('operation_type_id')
    def _onchange_operation_type_id(self):
        for record in self:
            record.unit_id = record.operation_type_id.unit_id

    @api.model_create_multi
    def create(self, vals_list):
        operation_types = self.env['wd.vas.operation.type']
        for vals in vals_list:
            operation_type = operation_types.browse(
                vals.get('operation_type_id')
            )
            if operation_type:
                vals['unit_id'] = operation_type.unit_id.id
        return super().create(vals_list)

    def write(self, vals):
        if 'operation_type_id' in vals:
            operation_type = self.env['wd.vas.operation.type'].browse(
                vals['operation_type_id']
            )
            vals = dict(vals, unit_id=operation_type.unit_id.id)
        return super().write(vals)

    @api.constrains('operation_type_id', 'unit_id')
    def _check_unit_matches_operation_type(self):
        for record in self:
            if (
                record.operation_type_id
                and record.unit_id != record.operation_type_id.unit_id
            ):
                raise ValidationError(
                    'Line unit must match the operation type unit.'
                )
