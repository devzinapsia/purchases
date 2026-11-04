=================================================
Restricción de creación de facturas desde compras
=================================================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

En Odoo estándar, cualquier usuario de **Compras** puede crear facturas de
proveedor desde una orden de compra, aunque no tenga acceso a
**Contabilidad**: la factura queda en borrador y ese usuario después no la
puede confirmar ni hacer nada más con ella.

Este módulo agrega el permiso adicional **Compras: permite crear factura**, que
se tilda o destilda por usuario. Solo quien lo tiene puede crear facturas de
proveedor desde Compras:

* En el formulario de la orden de compra se ocultan los botones
  **Crear factura** y **Subir factura**.
* En la lista de órdenes de compra se ocultan **Crear facturas** y
  **Subir factura** (este último aparece al seleccionar órdenes).
* Además, el servidor rechaza la acción **Crear factura** de la orden de
  compra (``action_create_invoice``) con el mensaje *"No tenés permiso para
  crear facturas de proveedor. Comunicate con el equipo de contabilidad."*,
  venga del botón que venga o de una llamada RPC.

El permiso **nace tildado**: al instalar el módulo (o al actualizarlo desde la
versión 19.0.1.0.0) se les da a todos los usuarios internos, y los usuarios
nuevos también lo reciben. Instalarlo no le cambia nada a nadie; la restricción
se aplica cuando se le destilda el permiso a un usuario.

Los usuarios con permisos de **Facturación** (``account.group_account_invoice``
o cualquier grupo que lo incluya) siempre lo tienen y no se les puede quitar.
Las acciones automáticas que corren como superusuario tampoco se bloquean.

No cambia los permisos de acceso (``ir.model.access``): los usuarios de Compras
siguen viendo las facturas vinculadas a sus órdenes.

El botón genérico **Subir** de la lista y del kanban de Compras no se toca:
crea órdenes de compra a partir de documentos, no facturas.

**Limitación:** el módulo no impide crear una factura de proveedor *a mano*
(por ejemplo, con **Nuevo** desde el botón inteligente **Facturas** de una
orden que ya tiene facturas), porque Odoo les da a los usuarios de Compras
permiso de creación sobre ``account.move``. Cerrar eso implica tocar
``ir.model.access``, lo que rompe contadores y botones de facturas en la orden
de compra, y queda fuera del alcance de este módulo.

**Tests de Odoo afectados:** con este módulo instalado fallan, a propósito,
``purchase.tests.test_access_rights`` ``test_create_purchase_order`` y
``test_read_purchase_order``, porque crean una factura desde una orden de
compra con un usuario de Compras creado sin este permiso.

**Table of contents**

.. contents::
   :local:

Configuración
=============

Para que un usuario **no** pueda crear facturas desde Compras:

#. Activar el modo desarrollador.
#. Ir a **Ajustes > Usuarios y compañías > Usuarios** y abrir el usuario.
#. En **Permisos adicionales**, destildar **Compras: permite crear factura**.

Para volver a permitirlo, tildarlo de nuevo. A los usuarios con permisos de
**Facturación** no se les puede destildar: lo tienen siempre.

Las facturas en borrador creadas antes de instalar el módulo no se borran:
las tiene que revisar un usuario de Contabilidad.

Uso
===

**Usuario sin el permiso**

#. Ir a **Compras > Pedidos > Órdenes de compra** y abrir una orden confirmada.
#. No aparecen los botones **Crear factura** ni **Subir factura**.
#. En la lista, al seleccionar órdenes, no aparecen **Crear facturas** ni
   **Subir factura**.
#. Si igual intenta crear la factura desde la orden de compra (por ejemplo,
   con una llamada RPC), aparece el mensaje *"No tenés permiso para crear
   facturas de proveedor. Comunicate con el equipo de contabilidad."* y no se
   crea nada.

**Usuario con el permiso**

#. Trabaja igual que antes: **Crear factura** genera la factura de proveedor en
   borrador. Si no tiene permisos de Facturación, después la tiene que
   confirmar alguien de Contabilidad.

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
