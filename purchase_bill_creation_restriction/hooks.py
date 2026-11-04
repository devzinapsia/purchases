from odoo import Command

BILL_CREATION_GROUP = "purchase_bill_creation_restriction.group_purchase_create_bill"


def grant_bill_creation_to_internal_users(env):
    """The bill creation permission is born granted: give it to every internal
    user and to new users, so that installing the module doesn't change anyone's
    behavior. The restriction applies once an administrator unticks it on a user.

    New users get it through ``base.default_user_group``, set here and not in XML:
    that record is ``noupdate`` in ``base``, so a data file can't change it on an
    upgrade of this module.
    """
    group = env.ref(BILL_CREATION_GROUP)
    users = env["res.users"].with_context(active_test=False).search([("share", "=", False)])
    users.write({"group_ids": [Command.link(group.id)]})
    default_user_group = env.ref("base.default_user_group", raise_if_not_found=False)
    if default_user_group:
        default_user_group.implied_ids = [Command.link(group.id)]


def post_init_hook(env):
    grant_bill_creation_to_internal_users(env)
