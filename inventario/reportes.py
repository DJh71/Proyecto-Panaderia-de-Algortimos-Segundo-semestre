"""Reportes de consola con columnas alineadas."""
from abc import ABC, abstractmethod


class Reporte(ABC):
    """Base abstracta de los reportes: todos se generan con generar()."""

    def __init__(self, simbolo_moneda="Q"):
        """Recibe el símbolo de moneda."""
        self._simbolo = simbolo_moneda

    def formato_moneda(self, valor):
        """Formatea un número como dinero (ej. Q1,234.50)."""
        return f"{self._simbolo}{valor:,.2f}"

    @abstractmethod
    def generar(self):
        """Devuelve el reporte como texto."""


class ReporteInventario(Reporte):
    """Tabla de productos."""

    def __init__(self, productos, simbolo_moneda="Q"):
        """Recibe la lista de productos a mostrar."""
        super().__init__(simbolo_moneda)
        self._productos = list(productos)

    def generar(self):
        """Devuelve la tabla de productos con columnas alineadas."""
        if not self._productos:
            return "No hay productos para mostrar."
        linea = "-" * 76
        filas = [linea,
                 f"{'Código':<8}{'Nombre':<26}{'Categoría':<14}"
                 f"{'Precio':>11}{'Stock':>7}{'IVA':>10}",
                 linea]
        for p in self._productos:
            filas.append(
                f"{p.codigo:<8}{p.nombre[:25]:<26}{p.categoria[:13]:<14}"
                f"{self.formato_moneda(p.precio):>11}{p.stock:>7}"
                f"{p.calculadora.etiqueta:>10}"
            )
        filas.append(linea)
        return "\n".join(filas)


class ReporteVentas(Reporte):
    """Reporte de las ventas de un día."""

    def __init__(self, registro, dia, nombre_negocio, simbolo_moneda="Q"):
        """Recibe el RegistroVentas, el día 'YYYY-MM-DD' y el nombre del negocio."""
        super().__init__(simbolo_moneda)
        self._registro = registro
        self._dia = dia
        self._negocio = nombre_negocio

    def generar(self):
        """Devuelve el reporte del día con totales."""
        del_dia = self._registro.del_dia(self._dia)
        linea, separador = "=" * 92, "-" * 92
        filas = [linea,
                 f"{self._negocio.upper()} - REPORTE DE VENTAS DEL {self._dia}",
                 linea,
                 f"{'Fecha':<17}{'Código':<8}{'Producto':<24}{'Cant.':>6}"
                 f"{'Subtotal':>12}{'IVA':>11}{'Total':>14}",
                 separador]
        if not del_dia:
            return "\n".join(filas + ["No hay ventas registradas en este día.", linea])

        m = self.formato_moneda
        for v in del_dia:
            filas.append(
                f"{v.fecha:<17}{v.codigo:<8}{v.producto[:23]:<24}{v.cantidad:>6}"
                f"{m(v.subtotal):>12}{m(v.iva):>11}{m(v.total):>14}"
            )
        filas += [separador,
                  f"{'TOTALES':<49}{sum(v.cantidad for v in del_dia):>6}"
                  f"{m(sum(v.subtotal for v in del_dia)):>12}"
                  f"{m(sum(v.iva for v in del_dia)):>11}"
                  f"{m(sum(v.total for v in del_dia)):>14}",
                  f"Ventas realizadas: {len(del_dia)}",
                  linea]
        return "\n".join(filas)
