##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from markupsafe import Markup

from odoo import api, fields, models
from odoo.tools import float_compare, formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    billed_not_received_warning = fields.Html(
        string="Billed not received warning",
        compute="_compute_billed_not_received",
        sanitize=False,
    )
    is_billed_not_received = fields.Boolean(
        string="Billed not received",
        compute="_compute_billed_not_received",
        search="_search_is_billed_not_received",
        help="Vendor bill with at least one purchase order line billed beyond what was received.",
    )

    def _get_billed_not_received_lines(self):
        """Return (purchase line, billed qty, received qty) for each purchase
        order line of this vendor bill billed beyond what was received.

        The billed quantity adds up every non-cancelled bill and credit note
        of the purchase line, taking this bill's current (possibly unsaved)
        lines instead of their stored values, so the warning reacts while the
        user edits quantities.
        """
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        result = []
        bill_lines = self.invoice_line_ids.filtered("purchase_line_id")
        for purchase_line in bill_lines.purchase_line_id:
            billed = 0.0
            other_lines = purchase_line.invoice_lines.filtered(
                lambda aml: aml.move_id != self._origin and aml.move_id.state != "cancel"
            )
            for aml in other_lines | bill_lines.filtered(lambda aml: aml.purchase_line_id == purchase_line):
                qty = aml.product_uom_id._compute_quantity(aml.quantity, purchase_line.product_uom_id)
                billed += -qty if aml.move_id.move_type == "in_refund" else qty
            received = purchase_line.qty_received
            if float_compare(billed, received, precision_digits=precision) > 0:
                result.append((purchase_line, billed, received))
        return result

    @api.depends(
        "move_type",
        "state",
        "invoice_line_ids.quantity",
        "invoice_line_ids.product_uom_id",
        "invoice_line_ids.purchase_line_id.qty_received",
        "invoice_line_ids.purchase_line_id.qty_invoiced",
        "invoice_line_ids.purchase_line_id.product_qty",
    )
    def _compute_billed_not_received(self):
        for move in self:
            rows = []
            if move.move_type == "in_invoice" and move.state != "cancel":
                rows = move._get_billed_not_received_lines()
            move.is_billed_not_received = bool(rows)
            if not rows:
                move.billed_not_received_warning = False
                continue
            move.billed_not_received_warning = move._render_billed_not_received_warning(rows)

    def _render_billed_not_received_warning(self, rows):
        """Render the warning as a table: one row per purchase line with its
        ordered, received, pending receipt, billed and pending billing
        quantities (billed includes this bill)."""
        self.ensure_one()

        def fmt(qty):
            return formatLang(self.env, qty, dp="Product Unit")

        headers = [
            self.env._("Product"),
            self.env._("Purchase order"),
            self.env._("Ordered"),
            self.env._("Received"),
            self.env._("Pending receipt"),
            self.env._("Billed (incl. this bill)"),
            self.env._("Pending billing"),
        ]
        head = Markup("").join(Markup("<th>%s</th>") % header for header in headers)
        body = Markup("").join(
            Markup("<tr><td>%s</td><td>%s</td>%s</tr>")
            % (
                line.product_id.display_name or line.name,
                line.order_id.name,
                Markup("").join(
                    Markup("<td class='text-end'>%s</td>") % fmt(qty)
                    for qty in (
                        line.product_qty,
                        received,
                        max(line.product_qty - received, 0.0),
                        billed,
                        line.product_qty - billed,
                    )
                ),
            )
            for line, billed, received in rows
        )
        return Markup(
            "<strong>%s</strong>"
            "<table class='table table-sm table-borderless mb-0 mt-1 w-auto'>"
            "<thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
        ) % (self.env._("Billed more than received on the purchase order:"), head, body)

    def _search_is_billed_not_received(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            return NotImplemented
        precision = self.env["decimal.precision"].precision_get("Product Unit")
        purchase_lines = (
            self.env["purchase.order.line"]
            .search([("invoice_lines", "!=", False), ("display_type", "=", False)])
            .filtered(lambda line: float_compare(line.qty_invoiced, line.qty_received, precision_digits=precision) > 0)
        )
        bills = purchase_lines.invoice_lines.move_id.filtered(
            lambda move: move.move_type == "in_invoice" and move.state != "cancel"
        )
        positive = (operator == "=") == value
        return [("id", "in" if positive else "not in", bills.ids)]
