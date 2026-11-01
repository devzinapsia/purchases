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
