from odoo import api, models
from odoo.exceptions import UserError

from ..hooks import BILL_CREATION_GROUP

VENDOR_DOCUMENT_TYPES = ("in_invoice", "in_refund", "in_receipt")
INVOICING_GROUP = "account.group_account_invoice"
# Mixins whose fields are written implicitly by the user's chatter or by the
# OCR (followers, activities, main attachment, extraction state): updating
# them is not editing the bill, so they stay allowed.
FREE_FIELD_MIXINS = ("mail.thread.main.attachment", "mail.activity.mixin", "extract.mixin.with.words")


def _can_edit_vendor_bills(env):
    return env.su or env.user.has_group(BILL_CREATION_GROUP)


def _raise_cannot_modify(env):
    raise UserError(
        env._("You don't have permission to modify or delete vendor bills. Please contact the accounting team.")
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _vendor_bill_free_fields(self):
        free_fields = set()
        for mixin in FREE_FIELD_MIXINS:
            if mixin in self.env:
                free_fields |= set(self.env[mixin]._fields)
        return free_fields

    def _vendor_documents(self):
        return self.filtered(lambda move: move.move_type in VENDOR_DOCUMENT_TYPES)

    @api.model_create_multi
    def create(self, vals_list):
        if not _can_edit_vendor_bills(self.env):
            default_type = self.env.context.get("default_move_type", "entry")
            if any(vals.get("move_type", default_type) in VENDOR_DOCUMENT_TYPES for vals in vals_list):
                raise UserError(
                    self.env._(
                        "You don't have permission to create vendor bills. Please contact the accounting team."
                    )
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            not _can_edit_vendor_bills(self.env)
            and set(vals) - self._vendor_bill_free_fields()
            and self._vendor_documents()
        ):
            _raise_cannot_modify(self.env)
        return super().write(vals)

    def unlink(self):
        if not _can_edit_vendor_bills(self.env) and self._vendor_documents():
            _raise_cannot_modify(self.env)
        return super().unlink()

    def _check_vendor_bill_accounting_action(self):
        """Odoo only hides "Reset to draft" and "Cancel" in the view for users
        without invoicing rights: enforce it on vendor documents, like posting."""
        if not self.env.su and not self.env.user.has_group(INVOICING_GROUP) and self._vendor_documents():
            raise UserError(
                self.env._("Only accounting users can reset to draft or cancel vendor bills.")
            )

    def button_draft(self):
        self._check_vendor_bill_accounting_action()
        return super().button_draft()

    def button_cancel(self):
        self._check_vendor_bill_accounting_action()
        return super().button_cancel()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_vendor_bill_lines_editable(self, moves):
        if not _can_edit_vendor_bills(self.env) and moves._vendor_documents():
            _raise_cannot_modify(self.env)

    @api.model_create_multi
    def create(self, vals_list):
        if not _can_edit_vendor_bills(self.env):
            move_ids = {vals["move_id"] for vals in vals_list if vals.get("move_id")}
            self._check_vendor_bill_lines_editable(self.env["account.move"].browse(move_ids))
        return super().create(vals_list)

    def write(self, vals):
        self._check_vendor_bill_lines_editable(self.move_id)
        return super().write(vals)

    def unlink(self):
        self._check_vendor_bill_lines_editable(self.move_id)
        return super().unlink()
