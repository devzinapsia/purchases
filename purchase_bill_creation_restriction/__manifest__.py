{
    "name": "Restricción de creación de facturas desde compras",
    "summary": "Solo los usuarios con permisos de facturación pueden crear facturas de proveedor desde una orden de compra",
    "version": "19.0.1.0.0",
    "category": "Inventory/Purchase",
    "license": "AGPL-3",
    "author": "Zinapsia",
    "website": "https://www.zinapsia.com",
    "depends": [
        "purchase_ux",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "purchase_bill_creation_restriction/static/src/views/*.js",
            "purchase_bill_creation_restriction/static/src/views/*.xml",
        ],
    },
    "auto_install": False,
    "application": False,
    "installable": True,
}
