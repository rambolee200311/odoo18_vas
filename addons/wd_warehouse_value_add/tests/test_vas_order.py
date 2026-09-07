# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVasOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.VasOperationType = cls.env['wd.vas.operation.type']
        cls.VasOrder = cls.env['wd.vas.order']
        cls.VasOrderLine = cls.env['wd.vas.order.line']
        cls.ChargeUnit = cls.env['world.depot.charge.unit']
        cls.Warehouse = cls.env['stock.warehouse']
        cls.unit = cls.ChargeUnit.create({'name': 'Hour'})
        cls.warehouse = cls.Warehouse.search([], limit=1)
        if not cls.warehouse:
            cls.warehouse = cls.Warehouse.create({
                'name': 'VAS Test Warehouse',
                'code': 'VASTEST',
            })
        cls.operation_type = cls.VasOperationType.create({
            'name': 'Labour',
            'code': 'LABOUR',
            'unit_id': cls.unit.id,
        })

    def _order_vals(self, **values):
        vals = {
            'order_type': 'inbound',
            'warehouse_order_billno': 'IN-001',
            'warehouse_id': self.warehouse.id,
        }
        vals.update(values)
        return vals

    def test_model_sequence_and_draft_state(self):
        order = self.VasOrder.create(self._order_vals())
        self.assertTrue(order.name.startswith('VAS/'))
        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.operator_id, self.env.user)

    def test_draft_without_lines_is_allowed(self):
        order = self.VasOrder.create(self._order_vals())
        self.assertFalse(order.line_ids)

    def test_operation_type_unit_snapshot(self):
        order = self.VasOrder.create(self._order_vals())
        line = self.VasOrderLine.create({
            'order_id': order.id,
            'operation_type_id': self.operation_type.id,
            'quantity_time': 0,
        })
        self.assertEqual(line.unit_id, self.unit)

    def test_explicit_relation_structure(self):
        fields_by_type = self.env['wd.vas.order']._fields
        self.assertEqual(
            fields_by_type['inbound_order_id'].comodel_name,
            'world.depot.inbound.order',
        )
        self.assertEqual(
            fields_by_type['outbound_order_id'].comodel_name,
            'world.depot.outbound.order',
        )
        self.assertEqual(
            fields_by_type['transfer_order_id'].comodel_name,
            'world.depot.transfer.order',
        )

    def test_relation_type_consistency(self):
        order = self.VasOrder.new(self._order_vals(
                order_type='outbound',
                inbound_order_id=1,
            ))
        with self.assertRaises(ValidationError):
            order._check_order_relation_consistency()

    def test_unique_constraints(self):
        with self.assertRaises(ValidationError):
            self.VasOperationType.create({
                'name': 'Labour Duplicate',
                'code': 'LABOUR',
                'unit_id': self.unit.id,
            })
        self.VasOrder.create(self._order_vals(name='VAS/DUPLICATE'))
        with self.assertRaises(ValidationError):
            self.VasOrder.create(self._order_vals(name='VAS/DUPLICATE'))
