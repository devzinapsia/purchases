from odoo.exceptions import UserError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestBillCreationRestriction(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.company_data["company"]
        user_values = {"company_id": company.id, "company_ids": [(6, 0, company.ids)]}
        cls.purchase_user = new_test_user(
            cls.env, login="purchase_no_billing", groups="purchase.group_purchase_user", **user_values
        )
        cls.billing_purchase_user = new_test_user(
            cls.env,
            login="purchase_billing",
            groups="purchase.group_purchase_user,account.group_account_invoice",
            **user_values,
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "purchase_method": "purchase",
                "standard_price": 10.0,
            }
        )

    def _confirmed_order(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_a.id,
                "order_line": [(0, 0, {"product_id": self.product.id, "product_qty": 4, "price_unit": 10.0})],
            }
        )
        order.button_confirm()
        self.assertEqual(order.invoice_status, "to invoice")
        return order

    def _bill_count(self):
        return self.env["account.move"].search_count([("move_type", "in", ("in_invoice", "in_refund"))])

    def test_user_without_billing_group_is_blocked(self):
        self.assertFalse(self.purchase_user.has_group("account.group_account_invoice"))
        order = self._confirmed_order()
        bill_count = self._bill_count()
        try:
            order.with_user(self.purchase_user).action_create_invoice()
        except UserError as error:
            self.assertIn("You don't have permission to create vendor bills", str(error))
        else:
            self.fail("A purchase user without invoicing rights must not create vendor bills")
        self.assertFalse(order.invoice_ids)
        self.assertEqual(self._bill_count(), bill_count)

    def test_user_with_billing_group_creates_bill(self):
        order = self._confirmed_order()
        order.with_user(self.billing_purchase_user).action_create_invoice()
        self.assertEqual(len(order.invoice_ids), 1)
        self.assertEqual(order.invoice_ids.state, "draft")
        self.assertEqual(order.invoice_ids.move_type, "in_invoice")

    def test_superuser_creates_bill(self):
        order = self._confirmed_order()
        order.with_user(self.purchase_user).sudo().action_create_invoice()
        self.assertEqual(len(order.invoice_ids), 1)
        self.assertEqual(order.invoice_ids.state, "draft")

    def _arch(self, user, view_type, view_xmlid=None):
        view_id = self.env.ref(view_xmlid).id if view_xmlid else None
        return self.env["purchase.order"].with_user(user).get_view(view_id=view_id, view_type=view_type)["arch"]

    def test_views_hide_bill_creation(self):
        form_arch = self._arch(self.purchase_user, "form")
        self.assertNotIn("action_create_invoice", form_arch)
        self.assertNotIn("purchase_file_uploader", form_arch)
        list_arch = self._arch(self.purchase_user, "list", "purchase.purchase_order_view_tree")
        self.assertNotIn("action_create_invoice", list_arch)

    def test_views_keep_bill_creation_for_billing_users(self):
        form_arch = self._arch(self.billing_purchase_user, "form")
        self.assertEqual(form_arch.count('name="action_create_invoice"'), 2)
        self.assertIn("purchase_file_uploader", form_arch)
        list_arch = self._arch(self.billing_purchase_user, "list", "purchase.purchase_order_view_tree")
        self.assertIn("action_create_invoice", list_arch)
