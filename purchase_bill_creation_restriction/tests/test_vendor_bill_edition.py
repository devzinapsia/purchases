from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from ..hooks import BILL_CREATION_GROUP


@tagged("post_install", "-at_install")
class TestVendorBillEdition(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.company_data["company"]
        user_values = {"company_id": company.id, "company_ids": [(6, 0, company.ids)]}
        cls.purchase_user = new_test_user(
            cls.env, login="bill_no_permission", groups="purchase.group_purchase_manager", **user_values
        )
        cls.permitted_purchase_user = new_test_user(
            cls.env,
            login="bill_with_permission",
            groups=f"purchase.group_purchase_manager,{BILL_CREATION_GROUP}",
            **user_values,
        )
        cls.accountant = new_test_user(
            cls.env,
            login="bill_accountant",
            groups="purchase.group_purchase_user,account.group_account_invoice",
            **user_values,
        )
        cls.draft_bill = cls.init_invoice("in_invoice", products=cls.product_a)
        cls.posted_bill = cls.init_invoice("in_invoice", products=cls.product_a, post=True)

    def _assert_blocked(self, func, message):
        try:
            func()
        except UserError as error:
            self.assertIn(message, str(error))
        else:
            self.fail(f"Expected UserError: {message}")

    def _bill_vals(self):
        return {
            "move_type": "in_invoice",
            "partner_id": self.partner_a.id,
            "invoice_line_ids": [Command.create({"product_id": self.product_a.id, "price_unit": 10.0})],
        }

    # --- users without the permission: vendor bills are read-only ---

    def test_without_permission_cannot_create_bill(self):
        moves = self.env["account.move"].with_user(self.purchase_user)
        self._assert_blocked(lambda: moves.create(self._bill_vals()), "permission to create vendor bills")
        self._assert_blocked(
            lambda: moves.with_context(default_move_type="in_invoice").create({"partner_id": self.partner_a.id}),
            "permission to create vendor bills",
        )

    def test_without_permission_cannot_modify_or_delete_bill(self):
        draft = self.draft_bill.with_user(self.purchase_user)
        message = "permission to modify or delete vendor bills"
        self._assert_blocked(lambda: draft.write({"ref": "Changed"}), message)
        self._assert_blocked(lambda: draft.invoice_line_ids.write({"price_unit": 99.0}), message)
        self._assert_blocked(
            lambda: draft.write({"invoice_line_ids": [Command.create({"product_id": self.product_a.id})]}), message
        )
        self._assert_blocked(lambda: draft.unlink(), message)
        self._assert_blocked(lambda: self.posted_bill.with_user(self.purchase_user).write({"narration": "x"}), message)
        self.assertNotEqual(self.draft_bill.ref, "Changed")
        self.assertTrue(self.draft_bill.exists())

    def test_without_permission_can_use_chatter(self):
        draft = self.draft_bill.with_user(self.purchase_user)
        attachment = self.env["ir.attachment"].with_user(self.purchase_user).create(
            {"name": "bill.pdf", "raw": b"%PDF-1.4 test", "res_model": "account.move", "res_id": draft.id}
        )
        draft.message_post(body="Please check", attachment_ids=attachment.ids)
        draft.activity_schedule("mail.mail_activity_data_todo", user_id=self.accountant.id)
        self.assertEqual(self.draft_bill.message_main_attachment_id, attachment)

    # --- users with the permission but without invoicing rights ---

    def test_with_permission_can_create_and_edit_draft_bill(self):
        bill = self.env["account.move"].with_user(self.permitted_purchase_user).create(self._bill_vals())
        bill.write({"ref": "Edited"})
        bill.invoice_line_ids.write({"price_unit": 20.0})
        self.assertEqual(bill.ref, "Edited")
        bill.unlink()
        self.assertFalse(bill.exists())

    def test_without_invoicing_rights_cannot_reset_or_cancel(self):
        message = "Only accounting users can reset to draft or cancel vendor bills"
        posted = self.posted_bill.with_user(self.permitted_purchase_user)
        self._assert_blocked(lambda: posted.button_draft(), message)
        self._assert_blocked(lambda: posted.button_cancel(), message)
        self._assert_blocked(lambda: self.draft_bill.with_user(self.permitted_purchase_user).button_cancel(), message)
        self.assertEqual(self.posted_bill.state, "posted")
        self.assertEqual(self.draft_bill.state, "draft")

    # --- invoicing users and superuser keep working ---

    def test_invoicing_user_can_reset_and_cancel(self):
        posted = self.posted_bill.with_user(self.accountant)
        posted.button_draft()
        self.assertEqual(self.posted_bill.state, "draft")
        posted.button_cancel()
        self.assertEqual(self.posted_bill.state, "cancel")

    def test_superuser_is_not_blocked(self):
        bill = self.env["account.move"].with_user(self.purchase_user).sudo().create(self._bill_vals())
        bill.write({"ref": "Sudo"})
        self.posted_bill.with_user(self.purchase_user).sudo().button_draft()
        self.assertEqual(self.posted_bill.state, "draft")
