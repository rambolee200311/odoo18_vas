# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VasOrder(models.Model):
    _name = 'wd.vas.order'
    _description = 'Warehouse Value Add Order'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='VAS Order',
        required=True,
        readonly=True,
        copy=False,
        default='New',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
        readonly=True,
    )
    order_type = fields.Selection(
        [
            ('inbound', 'Inbound'),
            ('outbound', 'Outbound'),
            ('transfer', 'Transfer'),
        ],
        string='Warehouse Order Type',
        required=True,
        tracking=True,
    )
    inbound_order_id = fields.Many2one(
        'world.depot.inbound.order',
        string='Inbound Order',
        ondelete='restrict',
    )
    outbound_order_id = fields.Many2one(
        'world.depot.outbound.order',
        string='Outbound Order',
        ondelete='restrict',
    )
    transfer_order_id = fields.Many2one(
        'world.depot.transfer.order',
        string='Transfer Order',
        ondelete='restrict',
    )
    warehouse_order_billno = fields.Char(
        string='Warehouse Order Bill No.',
        required=True,
    )
    warehouse_order_display = fields.Char(
        string='Warehouse Order',
        compute='_compute_warehouse_order_display',
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        ondelete='restrict',
    )
    operator_id = fields.Many2one(
        'res.users',
        string='Operator',
        required=True,
        default=lambda self: self.env.user,
    )
    submitter_id = fields.Many2one(
        'res.users',
        string='Submitter',
        readonly=True,
        tracking=True,
    )
    submitted_at = fields.Datetime(
        string='Submitted At',
        readonly=True,
        tracking=True,
    )
    unsubmitted_by = fields.Many2one(
        'res.users',
        string='Unsubmitted By',
        readonly=True,
        tracking=True,
    )
    unsubmitted_at = fields.Datetime(
        string='Unsubmitted At',
        readonly=True,
        tracking=True,
    )
    cancelled_by = fields.Many2one(
        'res.users',
        string='Cancelled By',
        readonly=True,
        tracking=True,
    )
    cancelled_at = fields.Datetime(
        string='Cancelled At',
        readonly=True,
        tracking=True,
    )
    cancel_reason = fields.Text(
        string='Cancel Reason',
        tracking=True,
    )
    line_ids = fields.One2many(
        'wd.vas.order.line',
        'order_id',
        string='Lines',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'wd_vas_order_attachment_rel',
        'order_id',
        'attachment_id',
        string='Attachments',
    )
    notes = fields.Text(string='Notes', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = sequence.next_by_code('wd.vas.order') or 'New'
        return super().create(vals_list)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            duplicate = self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id),
            ], limit=1)
            if duplicate:
                raise ValidationError('VAS order name must be unique.')

    @api.depends(
        'inbound_order_id',
        'outbound_order_id',
        'transfer_order_id',
    )
    def _compute_warehouse_order_display(self):
        for record in self:
            order = (
                record.inbound_order_id
                or record.outbound_order_id
                or record.transfer_order_id
            )
            record.warehouse_order_display = order.display_name if order else False

    @api.constrains(
        'order_type',
        'inbound_order_id',
        'outbound_order_id',
        'transfer_order_id',
    )
    def _check_order_relation_consistency(self):
        relation_by_type = {
            'inbound': 'inbound_order_id',
            'outbound': 'outbound_order_id',
            'transfer': 'transfer_order_id',
        }
        relation_fields = tuple(relation_by_type.values())
        for record in self:
            populated = [
                field_name
                for field_name in relation_fields
                if record[field_name]
            ]
            if len(populated) > 1:
                raise ValidationError(
                    'Only one Warehouse Order relation may be set.'
                )
            expected_field = relation_by_type.get(record.order_type)
            if populated and populated[0] != expected_field:
                raise ValidationError(
                    'Warehouse Order relation must match the selected order type.'
                )
