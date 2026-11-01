=========================================
Aviso de facturado sin recibir en compras
=========================================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

Cuando los productos se facturan **sobre cantidades ordenadas**,
**Crear Factura** propone todo lo pedido aunque la mercadería todavía no haya
llegado. Es útil cuando el proveedor factura o pide un anticipo antes de
enviar, pero se pierde la referencia visual de cuánto se recibió.

Este módulo agrega un **aviso** en la factura de proveedor cuando alguna línea
de una orden de compra queda facturada por encima de lo recibido:

* Se muestra un banner amarillo arriba de la factura con una tabla: por cada
  producto y orden de compra, las cantidades **Pedido**, **Recibido**,
  **Pendiente de recibir**, **Facturado (con este comprobante)** y
  **Pendiente de facturar**. Por ejemplo, con una orden por 5, 2 recibidas, una
  primera factura por 2 y una segunda por las 3 restantes, la segunda muestra:
  pedido 5, recibido 2, pendiente de recibir 3, facturado 5, pendiente de
  facturar 0.
* Lo facturado suma todas las facturas y notas de crédito no canceladas de esa
  línea de compra, incluida la que se está cargando (aunque todavía no se haya
  guardado).
* Aparece en borrador y también en la factura confirmada, para verlo antes de
  pagar.
* Se va solo cuando se recibe la mercadería que faltaba.
* Agrega el filtro **Facturado sin recibir** en la lista de facturas de
  proveedor.

**No bloquea nada**: la factura se puede confirmar y pagar igual. Es solo un
aviso.

**Table of contents**

.. contents::
   :local:

Configuración
=============

No requiere configuración. El aviso aplica a cualquier factura de proveedor
vinculada a una orden de compra, sea cual sea la política de control del
producto.

Uso
===

**Al cargar una factura**

#. Desde la orden de compra, hacer clic en **Crear Factura** (o cargarla
   desde Contabilidad con **Autocompletar**).
#. Si se factura más de lo recibido, arriba de la factura aparece el aviso
   *"Se factura más de lo recibido en la orden de compra"* con la tabla de
   cantidades de cada producto: pedido, recibido, pendiente de recibir,
   facturado (con este comprobante) y pendiente de facturar.
#. Revisar si corresponde (por ejemplo, un anticipo o una factura antes del
   envío) y confirmar igual, o corregir las cantidades.

**Control periódico**

#. Ir a **Contabilidad > Proveedores > Facturas**.
#. En **Filtros**, elegir **Facturado sin recibir**.
#. La lista muestra las facturas con mercadería todavía pendiente de recibir.
   Revisarlas antes de pagar y reclamar al proveedor las entregas atrasadas.

Bug Tracker
===========

Los errores se registran en
`GitHub Issues <https://github.com/devzinapsia/purchases/issues>`_.
Antes de reportar uno nuevo, revisar si ya fue informado.

Credits
=======

Authors
-------

* Zinapsia

Maintainers
-----------

Este módulo es mantenido por Zinapsia.

Este módulo es parte del proyecto
`purchases <https://github.com/devzinapsia/purchases>`_.
