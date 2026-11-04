from odoo import models
from odoo.exceptions import UserError

from ..hooks import BILL_CREATION_GROUP


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self, attachment_ids=False):
        """Only users with the bill creation permission can create vendor bills
        from a PO (invoicing users always have it, through an implied group).

        Odoo grants purchase users create access on ``account.move``, so they can
        create draft bills they can't post afterwards. Every bill-creating entry
        point of the PO (form and list buttons, "Upload Bill") calls this method,
        so the check lives here. Superuser calls (sudo, crons) are not blocked.
        """
        if not self.env.su and not self.env.user.has_group(BILL_CREATION_GROUP):
            raise UserError(
                self.env._("You don't have permission to create vendor bills. Please contact the accounting team.")
            )
        return super().action_create_invoice(attachment_ids=attachment_ids)
