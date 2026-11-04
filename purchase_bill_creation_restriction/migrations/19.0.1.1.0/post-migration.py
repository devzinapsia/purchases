from odoo import SUPERUSER_ID, api

from odoo.addons.purchase_bill_creation_restriction.hooks import grant_bill_creation_to_internal_users


def migrate(cr, version):
    # Up to 19.0.1.0.0 the check was against the invoicing group; the new
    # permission is born granted to every internal user, like on a fresh install.
    env = api.Environment(cr, SUPERUSER_ID, {})
    grant_bill_creation_to_internal_users(env)
