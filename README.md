# Sistema de Inventario y Ventas — Panadería Las Migajas

- **Estudiante:** _(tu nombre)_
- **Carné:** _(tu carné)_
- **Curso / ciclo:** _(curso y ciclo)_

## Tema y regla de negocio
Sistema de consola para una panadería: inventario, ventas y reportes.
**Regla especial: cálculo del IVA.** Los precios ya incluyen el IVA (12 %). Al vender, el sistema
desglosa `subtotal = total / 1.12` e `iva = total - subtotal`. Los productos exentos no pagan IVA.
Ejemplo: 3 × Pan integral (Q6.50) → total Q19.50, subtotal Q17.41, IVA Q2.09.

## Cómo ejecutarlo
Requiere Python 3.8+ (solo biblioteca estándar). Desde la raíz del repositorio:

```bash
python main.py
```

## Estructura
```
main.py                 Punto de entrada
inventario/
  excepciones.py        Excepciones personalizadas
  reglas.py             Regla del IVA (clase abstracta + subclases)
  modelos.py            Producto y Venta
  inventario.py         Inventario y RegistroVentas
  persistencia.py       RepositorioCSV y Bitacora
  reportes.py           Reportes en consola
  app.py                Consola y SistemaInventario
datos/                  inventario.csv, ventas.csv y bitacora.log
docs/                   Diagramas UML y reflexión
evidencias/             Capturas de pruebas
```

## Clases
| Clase | Responsabilidad |
|---|---|
| `Producto` | Datos y validaciones de un producto; descuenta/agrega stock y desglosa el IVA |
| `Venta` | Registro inmutable de una venta (`@dataclass(frozen=True)`) |
| `Inventario` | Colección de productos: agregar, eliminar, buscar, ordenar, vender |
| `RegistroVentas` | Colección de ventas y filtro por día |
| `CalculadoraImpuesto` (abstracta) | Contrato para desglosar un total en subtotal e IVA |
| `ConIVA` / `SinIVA` | Calculadora con IVA 12 % / calculadora de productos exentos |
| `RepositorioCSV` | Lee y escribe inventario y ventas en CSV |
| `Bitacora` | Registra operaciones con fecha y hora (modo append) |
| `Reporte` (abstracta) | Base de los reportes (`generar()`) |
| `ReporteInventario` / `ReporteVentas` | Tablas alineadas de inventario y de ventas del día |
| `Consola` | Lectura validada de datos por teclado |
| `SistemaInventario` | Menú y coordinación de todos los objetos |
| `InventarioError` y 6 subclases | Excepciones propias del sistema |

## Diagramas UML
### Casos de uso
![Diagrama de casos de uso](docs/casos_de_uso.png)

### Clases
![Diagrama de clases](docs/diagrama_clases.png)

Fuentes editables: `docs/casos_de_uso.puml` y `docs/diagrama_clases.mmd`.

## Ejemplo de uso
```
Elige una opción: 3

--- Registrar venta ---
Código del producto: PAS001
Pastel de chocolate | Q85.00 | stock disponible: 8
Cantidad a vender: 2

Venta registrada
  Producto : Pastel de chocolate (PAS001)
  Cantidad : 2
  Subtotal :      Q151.79
  IVA (12%)      :       Q18.21
  TOTAL    :      Q170.00
```

## Reflexión
Ver [docs/reflexion.md](docs/reflexion.md).
