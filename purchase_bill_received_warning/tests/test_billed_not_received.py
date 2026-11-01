import re

from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestBilledNotReceived(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test storable product",
                "is_storable": True,
                "purchase_method": "purchase",
                "standard_price": 10.0,
            }
        )

    def _confirm_po(self, qty):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [(0, 0, {"product_id": self.product.id, "product_qty": qty, "price_unit": 10.0})],
            }
        )
        order.button_confirm()
        return order

    def _receive(self, order, qty):
        receipt = order.picking_ids.filtered(lambda picking: picking.state not in ("done", "cancel"))
        receipt.move_ids.quantity = qty
        receipt.move_ids.picked = True
        # _action_done() keeps the rest in a backorder, like "Create backorder"
        receipt._action_done()

    def _create_bill(self, order):
        action = order.action_create_invoice()
        bill = self.env["account.move"].browse(action["res_id"])
        bill.invoice_date = fields.Date.today()
        return bill

    def test_warning_when_billed_more_than_received(self):
        order = self._confirm_po(10)
        self._receive(order, 2)
        bill = self._create_bill(order)

        self.assertEqual(bill.invoice_line_ids.quantity, 10)
        self.assertTrue(bill.is_billed_not_received)
        self.assertIn("Billed more than received", bill.billed_not_received_warning)
        self.assertIn(order.name, bill.billed_not_received_warning)
        self.assertIn(bill, self.env["account.move"].search([("is_billed_not_received", "=", True)]))

    def test_no_warning_when_received(self):
        order = self._confirm_po(10)
        self._receive(order, 10)
        bill = self._create_bill(order)

        self.assertFalse(bill.is_billed_not_received)
        self.assertFalse(bill.billed_not_received_warning)
        self.assertNotIn(bill, self.env["account.move"].search([("is_billed_not_received", "=", True)]))
        self.assertIn(bill, self.env["account.move"].search([("is_billed_not_received", "=", False)]))

    def test_warning_reacts_to_unsaved_quantity(self):
        order = self._confirm_po(10)
        self._receive(order, 2)
        bill = self._create_bill(order)

        with Form(bill) as bill_form:
            with bill_form.invoice_line_ids.edit(0) as line_form:
                line_form.quantity = 2
            self.assertFalse(bill_form.is_billed_not_received)

        self.assertFalse(bill.is_billed_not_received)

    def test_warning_clears_once_rest_is_received(self):
        order = self._confirm_po(10)
        self._receive(order, 2)
        bill = self._create_bill(order)
        self.assertTrue(bill.is_billed_not_received)

        self._receive(order, 8)

        self.assertFalse(bill.is_billed_not_received)

    def test_previous_bills_are_added_up(self):
        order = self._confirm_po(10)
        self._receive(order, 5)
        first_bill = self._create_bill(order)
        first_bill.invoice_line_ids.quantity = 5
        first_bill.action_post()
        self.assertFalse(first_bill.is_billed_not_received)

        second_bill = self._create_bill(order)
        second_bill.invoice_line_ids.quantity = 1

        self.assertTrue(second_bill.is_billed_not_received, "5 already billed + 1 now exceeds the 5 received")

    def test_warning_shows_pending_quantities(self):
        """PO for 5, 2 received, a first bill for 2 and a second one proposing
        the remaining 3: the warning shows ordered, received, pending
        receipt, billed (with this bill) and pending billing."""
        order = self._confirm_po(5)
        self._receive(order, 2)
        first_bill = self._create_bill(order)
        first_bill.invoice_line_ids.quantity = 2
        first_bill.action_post()
        self.assertFalse(first_bill.is_billed_not_received)

        second_bill = self._create_bill(order)
        self.assertEqual(second_bill.invoice_line_ids.quantity, 3)
        self.assertTrue(second_bill.is_billed_not_received)
        warning = second_bill.billed_not_received_warning
        for header in ("Ordered", "Received", "Pending receipt", "Billed (incl. this bill)", "Pending billing"):
            self.assertIn(header, warning)
        cells = re.findall(r"<td class='text-end'>([^<]*)</td>", warning)
        self.assertEqual(cells, ["5.00", "2.00", "3.00", "5.00", "0.00"])
