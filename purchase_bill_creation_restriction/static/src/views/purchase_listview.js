import { onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";
import { patch } from "@web/core/utils/patch";
import { PurchaseFileUploadListController } from "@purchase/views/purchase_listview";

// The list "Upload Bill" button is rendered from JS, so view `groups=` can't
// hide it: show it only to users who can create vendor bills.
patch(PurchaseFileUploadListController.prototype, {
    setup() {
        super.setup(...arguments);
        this.canCreateVendorBills = false;
        onWillStart(async () => {
            this.canCreateVendorBills = await user.hasGroup("account.group_account_invoice");
        });
    },
});
